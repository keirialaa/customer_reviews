import json
import os
import pandas as pd
from dotenv import load_dotenv
from flask import Flask, flash, render_template, request, redirect, url_for, jsonify
from services.data_processor import allowed_file, validate_upload_file, process_upload_data
from services.ml_engine import run_full_analysis

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ["FLASK_SECRET_KEY"]


def get_product_rankings(data, min_reviews=1): 
    if "rating" in data.columns:
        score_col = "rating"
        neutral_line = 3.0 
    else:
        sentiment_map = {"Positive": 1, "Neutral": 0, "Negative": -1}
        data["temp_score"] = data["sentiment"].map(sentiment_map)
        score_col = "temp_score"
        neutral_line = 0 

    # Overall rankings 
    overall_stats = data.groupby("product_name")[score_col].agg(["mean", "count"])
    
    # Filter by minimum reviews
    qualified = overall_stats[overall_stats["count"] >= min_reviews]
    
    # Separate the pool into potential Best and potential Worst
    best_pool = qualified[qualified["mean"] >= neutral_line]
    worst_pool = qualified[qualified["mean"] < neutral_line]

    # If the worst pool is empty (all products are good), 
    # we take the bottom of the best pool so the chart isn't blank
    if worst_pool.empty and not qualified.empty:
        worst_pool = qualified

    best_overall = best_pool.nlargest(3, "mean").index.tolist()
    worst_overall = worst_pool.nsmallest(3, "mean").index.tolist()

    # By category rankings 
    category_rankings = {}
    if "category" in data.columns:
        for cat in data["category"].unique():
            cat_data = data[data["category"] == cat]
            cat_stats = cat_data.groupby("product_name")[score_col].agg(["mean", "count"])
            cat_qual = cat_stats[cat_stats["count"] >= 1] 
            
            c_best_pool = cat_qual[cat_qual["mean"] >= neutral_line]
            c_worst_pool = cat_qual[cat_qual["mean"] < neutral_line]
            
            # If a category has ONLY good products, show the "least good" in Worst
            if c_worst_pool.empty and not cat_qual.empty:
                c_worst_pool = cat_qual

            category_rankings[cat] = {
                "best": c_best_pool.nlargest(3, "mean").index.tolist(),
                "worst": c_worst_pool.nsmallest(3, "mean").index.tolist()
            }

    return {
        "overall": {"best": best_overall, "worst": worst_overall},
        "by_category": category_rankings
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    # Validate the file 
    if "file" not in request.files:
        return redirect(url_for("index"))
    
    file = request.files["file"]
    
    if file and allowed_file(file.filename):
        if not os.path.exists("data"): os.makedirs("data")
        raw_path = "data/raw_upload.csv"
        file.save(raw_path)
        
        return redirect(url_for("dashboard"))
    
    flash("Invalid file type.")
    return redirect(url_for("index"))


@app.route("/dashboard")
def dashboard():
    if not os.path.exists("data/raw_upload.csv"):
        return redirect(url_for("index"))
    return render_template("dashboard.html")


@app.route("/analyze", methods=["GET"])
def analyze():
    raw_path = "data/raw_upload.csv"
    if not os.path.exists(raw_path):
        return jsonify({"error": "No file found"}), 400

    df = pd.read_csv(raw_path)
    
    # Validation and processing
    is_valid, error = validate_upload_file(df)
    if not is_valid:
        return jsonify({"error": error}), 400
    
    data_clean = process_upload_data(df)
    data = run_full_analysis(data_clean)
    
    #  Prepare Data for JSON response 
    total_count = len(data)
    stats_sent = data["sentiment"].value_counts().to_dict()

    # Product performance
    sentiment_map = {"Positive": 1, "Neutral": 0, "Negative": -1}
    total_counts = data.groupby("product_name").size()
    avg_sent_score = round(data["sentiment"].map(sentiment_map).mean(), 2)
    pos_counts = data[data["sentiment"] == "Positive"].groupby("product_name").size()
    pos_percentage = (pos_counts.div(total_counts, fill_value=0) * 100).nlargest(5)
    
    # Category chart
    cat_sentiment_df = data.groupby(["category", "sentiment"]).size().unstack(fill_value=0)
    
    # Sentiment over time
    time_data = {"has_time": False}
    if "review_date" in data.columns:
        data["review_date"] = pd.to_datetime(data["review_date"])
        time_series = data.groupby([pd.Grouper(key="review_date", freq="MS"), "sentiment"]).size().unstack(fill_value=0)
        time_data = {
            "has_time": True,
            "labels": time_series.index.strftime("%b %Y").tolist(),
            "pos": time_series["Positive"].tolist() if "Positive" in time_series else [0]*len(time_series),
            "neu": time_series["Neutral"].tolist() if "Neutral" in time_series else [0]*len(time_series),
            "neg": time_series["Negative"].tolist() if "Negative" in time_series else [0]*len(time_series),
        }

    return jsonify({
        "avg_score": avg_sent_score,
        "total_count": total_count,
        "pie": {
            "labels": ["Positive", "Neutral", "Negative"],
            "values": [int(stats_sent.get("Positive", 0)), int(stats_sent.get("Neutral", 0)), int(stats_sent.get("Negative", 0))]
        },
        "stacked": {
            "labels": cat_sentiment_df.index.tolist(),
            "pos": cat_sentiment_df["Positive"].tolist() if "Positive" in cat_sentiment_df else [],
            "neu": cat_sentiment_df["Neutral"].tolist() if "Neutral" in cat_sentiment_df else [],
            "neg": cat_sentiment_df["Negative"].tolist() if "Negative" in cat_sentiment_df else [],
        },
        "top5": pos_percentage.to_dict(),
        "time_series": time_data, 
        "rankings": get_product_rankings(data, 3),
    })





