# Customer Review Insights Dashboard

A Python-based analytical tool that uses RoBERTa for sentiment analysis, K-Means Clustering for automated product categorization, and BART for abstractive review summarization.

## Features

- Sentiment Analysis: Leverages a fine-tuned RoBERTa model to classify customer feedback.
- Product Clustering: Groups products into logical categories.
- Visualization: Dashboard built with Chart.js showing sentiment distribution and category rankings.
- AI Market Reports (notebook-only, not inlcuded in the UI): Generates "best"/"worst" product summaries using the BART-large-cnn model, providing cohesive insights instead of raw quote lists.

## Installation & Setup

1.  **Clone the repository**  
    Open your terminal and run:

```bash
git clone https://github.com/keirialaa/customer_reviews.git
cd customer_reviews
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Run the application**

```bash
   export FLASK_APP=app.py
   flask run
```

## Project Structure

- app.py: Flask application for the dashboard
- notebooks: Directory with Jupyter notebooks
- models/: Directory for local model configuration (ignored by Git per .gitignore)
- data/: Directory for input CSV files
- services/: Data processing and ML engine
