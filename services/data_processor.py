import pandas as pd 
ALLOWED_EXTENSIONS = {"csv"}


def allowed_file(filename):
    """
    Checks if:
    1. The filename contains a dot.
    2. The extension after the last dot is in the allowed list.
    """
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_upload_file(df):
    '''
    Checks if the required columns exist. 
    '''
    required_columns = ["product_name", "review_text"]
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        return False, f"Missing required columns: {', '.join(missing)}"
    return True, None 


def process_upload_data(df):
    '''
    Handles NaNs, typecasting, and feature engineering. 
    '''
    # Drop entries without a review
    df = df.dropna(subset=["review_text"])

    # Combine review title and text into one column 
    if "review_title" not in df.columns:
        df["full_text"] = df["review_text"]
    else:
        df["review_title"] = df["review_title"].fillna("")
        df["full_text"] = df["review_title"].astype(str) + " " + df["review_text"].astype(str)

    return df[["product_name", "full_text"]]

