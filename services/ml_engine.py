import os, re
import pandas as pd
import torch
from dotenv import load_dotenv
from openai import OpenAI
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL_PATH = "models/sentiment_model"

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
embedder = SentenceTransformer("all-MiniLM-L6-v2")


def get_sentiment(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
    prediction = int(torch.argmax(probs).item())
    labels = {0: "Negative", 1: "Neutral", 2: "Positive"}
    return labels[prediction]


def get_professional_label(text):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[
                {"role": "system", "content": "You are a retail data expert. Your task is to provide a single, professional 2-3 word category name that summarizes a list of products. Return ONLY the category name."},
                {"role": "user", "content": f"Product List:\n{text}"}
            ],
            temperature=0 
        )
        return (response.choices[0].message.content or "").strip()
    except:
        return "Uncategorized"


def distill_cluster(df, cluster_id):
    unique_names = df[df["cluster_id"] == cluster_id]["product_name"].unique()
    clean_set = set()
    for name in unique_names:
        clean_name = re.sub(r"[^a-zA-Z0-9\s]", " ", str(name))
        clean_name = " ".join(clean_name.split()[:10]).lower()
        clean_set.add(clean_name)
    return "\n- ".join(list(clean_set)[:10])


def run_full_analysis(df):
    # Run sentiment analysis
    df["sentiment"] = df["full_text"].apply(get_sentiment)

    # Embed strings 
    unique_names = df["product_name"].unique().tolist()
    embeddings = embedder.encode(unique_names)
    
    # Create clusters
    num_clusters = min(len(unique_names), 5) 
    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(embeddings)
    
    # Map cluster IDs to the dataframe
    name_to_id = dict(zip(unique_names, labels))
    df["cluster_id"] = df["product_name"].map(name_to_id)

    # Professional labeling 
    c_labels_map = {}
    existing_labels = set()
    
    for cluster_key in range(num_clusters):
        text_summary = distill_cluster(df, cluster_key)
        label = get_professional_label(text_summary)
        
        # Deduplicate labels
        if label in existing_labels:
            label = f"{label} ({cluster_key})"
        
        c_labels_map[cluster_key] = label
        existing_labels.add(label)

    # Final mapping to categories 
    df["category"] = df["cluster_id"].map(c_labels_map).fillna("Miscellaneous")

    return df