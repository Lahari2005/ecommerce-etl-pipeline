from pathlib import Path

import pandas as pd


# Project directories
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"


# Create processed directory if it doesn't exist
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)


# Input and output files
INPUT_FILE = RAW_DATA_DIR / "olist_orders_dataset.csv"
OUTPUT_FILE = PROCESSED_DATA_DIR / "cleaned_orders.csv"


def transform_orders():
    """
    Clean and transform the Olist orders dataset.
    """

    # Read raw data
    df = pd.read_csv(INPUT_FILE)

    print(f"Original rows: {len(df)}")

    # --------------------------------------------------
    # 1. Standardize column names
    # --------------------------------------------------

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # --------------------------------------------------
    # 2. Remove completely duplicated rows
    # --------------------------------------------------

    duplicate_count = df.duplicated().sum()

    print(f"Duplicate rows found: {duplicate_count}")

    df = df.drop_duplicates()

    # --------------------------------------------------
    # 3. Convert timestamp columns to datetime
    # --------------------------------------------------

    date_columns = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]

    for column in date_columns:
        df[column] = pd.to_datetime(
            df[column],
            errors="coerce"
        )

    # --------------------------------------------------
    # 4. Standardize order status
    # --------------------------------------------------

    df["order_status"] = (
        df["order_status"]
        .str.strip()
        .str.lower()
    )

    # --------------------------------------------------
    # 5. Remove records without an order ID
    # --------------------------------------------------

    missing_order_ids = df["order_id"].isna().sum()

    print(f"Missing order IDs: {missing_order_ids}")

    df = df.dropna(subset=["order_id"])

    # --------------------------------------------------
    # 6. Remove duplicate order IDs
    # --------------------------------------------------

    duplicate_order_ids = df["order_id"].duplicated().sum()

    print(f"Duplicate order IDs: {duplicate_order_ids}")

    df = df.drop_duplicates(
        subset=["order_id"],
        keep="first"
    )

    # --------------------------------------------------
    # 7. Create useful derived columns
    # --------------------------------------------------

    df["purchase_date"] = (
        df["order_purchase_timestamp"].dt.date
    )

    df["purchase_year"] = (
        df["order_purchase_timestamp"].dt.year
    )

    df["purchase_month"] = (
        df["order_purchase_timestamp"].dt.month
    )

    # --------------------------------------------------
    # 8. Calculate delivery time
    # --------------------------------------------------

    df["delivery_days"] = (
        df["order_delivered_customer_date"]
        - df["order_purchase_timestamp"]
    ).dt.total_seconds() / (60 * 60 * 24)

    # --------------------------------------------------
    # 9. Calculate whether delivery was late
    # --------------------------------------------------

    df["is_late"] = (
        df["order_delivered_customer_date"]
        > df["order_estimated_delivery_date"]
    )

    # --------------------------------------------------
    # 10. Save transformed data
    # --------------------------------------------------

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(f"Final rows: {len(df)}")
    print(f"Saved transformed data to: {OUTPUT_FILE}")


if __name__ == "__main__":
    transform_orders()