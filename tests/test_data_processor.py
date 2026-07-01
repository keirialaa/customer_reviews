import pandas as pd
import pytest

from services.data_processor import allowed_file, process_upload_data, validate_upload_file


@pytest.mark.parametrize(
    "filename,expected",
    [
        ("reviews.csv", True),
        ("reviews.CSV", True),
        ("reviews.txt", False),
        ("reviews", False),
    ],
)
def test_allowed_file(filename, expected):
    assert allowed_file(filename) is expected


def test_validate_upload_file_missing_columns():
    df = pd.DataFrame({"product_name": ["Widget"]})
    is_valid, error = validate_upload_file(df)
    assert is_valid is False
    assert "review_text" in error


def test_validate_upload_file_ok():
    df = pd.DataFrame({"product_name": ["Widget"], "review_text": ["Great product"]})
    is_valid, error = validate_upload_file(df)
    assert is_valid is True
    assert error is None


def test_process_upload_data_drops_missing_reviews():
    df = pd.DataFrame({
        "product_name": ["Widget", "Gadget"],
        "review_text": ["Great product", None],
    })
    result = process_upload_data(df)
    assert len(result) == 1
    assert result.iloc[0]["full_text"] == "Great product"


def test_process_upload_data_combines_title_and_text():
    df = pd.DataFrame({
        "product_name": ["Widget"],
        "review_title": ["Love it"],
        "review_text": ["Works great"],
    })
    result = process_upload_data(df)
    assert result.iloc[0]["full_text"] == "Love it Works great"
