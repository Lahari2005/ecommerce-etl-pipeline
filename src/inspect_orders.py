from pathlib import Path

import pandas as pd


# Project directories
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"


# File path
ORDERS_FILE = RAW_DATA_DIR / "olist_orders_dataset.csv"


def inspect_orders():
    """Inspect the raw orders dataset."""

    df = pd.read_csv(ORDERS_FILE)

    print("\n===== DATASET SHAPE =====")
    print(df.shape)

    print("\n===== COLUMN NAMES =====")
    print(df.columns.tolist())

    print("\n===== DATA TYPES =====")
    print(df.dtypes)

    print("\n===== MISSING VALUES =====")
    print(df.isnull().sum())

    print("\n===== DUPLICATE ROWS =====")
    print(df.duplicated().sum())

    print("\n===== ORDER STATUS VALUES =====")
    print(df["order_status"].value_counts())

    print("\n===== FIRST 5 ROWS =====")
    print(df.head())


if __name__ == "__main__":
    inspect_orders()