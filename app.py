import json
import os 
import pandas as pd 
from flask import Flask, flash, render_template, request, redirect, url_for
from services.data_processor import allowed_file, validate_upload_file, process_upload_data
from services.ml_engine import run_full_analysis

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return redirect(request.url)
    
    file = request.files["file"]
    
    # Validate file extension
    if file and allowed_file(file.filename):
        df = pd.read_csv(file)
        
        # Validate schema 
        is_valid, error = validate_upload_file(df)
        if not is_valid:
            return render_template("index.html", error=error)
        
        # Clean and process data 
        data_clean = process_upload_data(df)
        
        # Run review analysis 
        data_processed = run_full_analysis(data_clean)
        
        # Save results to a temporary CSV for the dashboard 
        data_processed.to_csv("data/results.csv", index=False)
        
        return redirect(url_for("dashboard"))
    
    return render_template("index.html", error="Invalid file type.")


@app.route("/dashboard")
def dashboard():
    # Read preprocessed data from file 
    if not os.path.exists("data/results.csv"):
        return redirect(url_for("index"))
    data = pd.read_csv("data/results.csv")

    print(data.columns)

    # Calculate stats for the dashboard 
    total_count = len(data)
    stats_sent = data["sentiment"].value_counts().to_dict()

    total_counts = data.groupby("product_name").size()
    pos_counts = data[data["sentiment"] == "Positive"].groupby("product_name").size()
    pos_percentage = pos_counts.div(total_counts, fill_value=0) * 100
    top_5_percent = pos_percentage[total_counts > 0].nlargest(5)

    cat_sentiment_df = data.groupby(["category", "sentiment"]).size().unstack(fill_value=0)
    chart_labels2 = cat_sentiment_df.index.tolist()

    pos_data = cat_sentiment_df["Positive"].tolist() if "Positive" in cat_sentiment_df else [0]*len(chart_labels2)
    neu_data = cat_sentiment_df["Neutral"].tolist() if "Neutral" in cat_sentiment_df else [0]*len(chart_labels2)
    neg_data = cat_sentiment_df["Negative"].tolist() if "Negative" in cat_sentiment_df else [0]*len(chart_labels2)

    # Create chart labels 
    order = ["Positive", "Neutral", "Negative"]
    ordered_stats = {sentiment: int(stats_sent.get(sentiment, 0)) for sentiment in order}
    chart_labels1 = list(ordered_stats.keys())
    chart_data1 = list(ordered_stats.values()) 

    # Sentiment over time data 
    if "review_date" in data.columns:
        data["review_date"] = pd.to_datetime(data["review_date"])
        time_series = data.groupby([pd.Grouper(key="review_date", freq="MS"), "sentiment"]).size().unstack(fill_value=0)
        time_labels = time_series.index.strftime("%b %Y").tolist()

        time_pos = time_series["Positive"].tolist() if "Positive" in time_series else [0]*len(time_labels)
        time_neu = time_series["Neutral"].tolist() if "Neutral" in time_series else [0]*len(time_labels)
        time_neg = time_series["Negative"].tolist() if "Negative" in time_series else [0]*len(time_labels)

        has_time_data = True
    else:
        time_labels, time_pos, time_neu, time_neg = [], [], [], []
        has_time_data = False

    return render_template(
        "dashboard.html",
        total_count=total_count,
        labels1=json.dumps(chart_labels1), 
        values1=json.dumps(chart_data1), 
        labels2=json.dumps(chart_labels2),
        pos_values=json.dumps(pos_data),
        neu_values=json.dumps(neu_data),
        neg_values=json.dumps(neg_data),
        top5=top_5_percent,
        has_time_data=has_time_data,
        time_labels=json.dumps(time_labels),
        time_pos=json.dumps(time_pos),
        time_neu=json.dumps(time_neu),
        time_neg=json.dumps(time_neg)
    )





