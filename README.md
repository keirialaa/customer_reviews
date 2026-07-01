# Customer Review Insights Dashboard

A Python-based analytical tool that uses RoBERTa for sentiment analysis, K-Means clustering for automated product categorization, and BART for abstractive review summarization.

## Features

- **Sentiment Analysis**: Classifies customer reviews (Positive / Neutral / Negative) using a fine-tuned RoBERTa model.
- **Product Clustering**: Groups products into logical categories using sentence embeddings + K-Means, then labels each cluster with GPT-4o-mini.
- **Visualization**: Interactive dashboard (Chart.js) showing sentiment distribution, category rankings, and sentiment trends over time.
- **AI Market Reports** (notebook-only, not wired into the UI): Generates "best"/"worst" product summaries using `facebook/bart-large-cnn`, producing cohesive write-ups instead of raw quote lists.

## Project Structure

```
app.py                  # Flask application / API routes
services/
  data_processor.py      # Upload validation & cleaning
  ml_engine.py           # Sentiment, clustering, and category labeling
models/sentiment_model/  # Fine-tuned RoBERTa checkpoint (not included, see below)
notebooks/               # Model training & experimentation
  classifier_full_dataset.ipynb
  clustering.ipynb
  review_summarization.ipynb
templates/, static/       # Dashboard UI
docs/Project Report.pdf   # Write-up of the approach and findings
```

## Installation & Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/keirialaa/customer_reviews.git
   cd customer_reviews
   ```

2. **Create a virtual environment and install dependencies**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt        # runtime only
   # or, to also run the notebooks / tests:
   pip install -r requirements-dev.txt
   ```

3. **Configure environment variables**

   Copy the example file and fill in your own keys:

   ```bash
   cp .env.example .env
   ```

   | Variable           | Required               | Purpose                                                                  |
   | ------------------ | ---------------------- | ------------------------------------------------------------------------ |
   | `FLASK_SECRET_KEY` | Yes                    | Flask session signing key. Any random string works locally.              |
   | `OPENAI_API_KEY`   | Yes                    | Used by GPT-4o-mini to generate cluster category labels.                 |
   | `HF_TOKEN`         | Only for the notebooks | Hugging Face token used when downloading/pushing models in `notebooks/`. |

4. **Provide the sentiment model**

   `models/sentiment_model/` is not committed to the repo (the checkpoint is ~500MB). To get it locally, either:
   - Run `notebooks/classifier_full_dataset.ipynb` end-to-end, which fine-tunes RoBERTa and saves the checkpoint to `models/sentiment_model/`, or
   - Point `MODEL_PATH` in `services/ml_engine.py` at a Hugging Face Hub model ID instead of a local path.

5. **Run the application**

   ```bash
   export FLASK_APP=app.py
   flask run
   ```

   Then open `http://127.0.0.1:5000`, upload a CSV with at least `product_name` and `review_text` columns, and view the dashboard.

## Running tests

```bash
pip install -r requirements-dev.txt
pytest
```

## License

MIT — see [LICENSE](LICENSE).
