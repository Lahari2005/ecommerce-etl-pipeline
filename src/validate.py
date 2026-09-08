from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"

INPUT_FILE = PROCESSED_DATA_DIR / "cleaned_orders.csv"


def validate_orders():
    df = pd.read_csv(INPUT_FILE)

    validation_passed = True

    print("===== DATA VALIDATION =====")

    # 1. Record count
    print(f"Record count: {len(df)}")

    if len(df) == 0:
        print("FAIL: Dataset is empty")
        validation_passed = False
    else:
        print("PASS: Dataset contains records")

    # 2. Null order IDs
    null_order_ids = df["order_id"].isnull().sum()

    print(f"Null order IDs: {null_order_ids}")

    if null_order_ids > 0:
        print("FAIL: Null order IDs found")
        validation_passed = False
    else:
        print("PASS: No null order IDs")

    # 3. Duplicate order IDs
    duplicate_order_ids = df["order_id"].duplicated().sum()

    print(f"Duplicate order IDs: {duplicate_order_ids}")

    if duplicate_order_ids > 0:
        print("FAIL: Duplicate order IDs found")
        validation_passed = False
    else:
        print("PASS: Order IDs are unique")

    # 4. Order status validation
    valid_statuses = {
        "delivered",
        "shipped",
        "canceled",
        "invoiced",
        "processing",
        "approved",
        "unavailable",
        "created"
    }

    invalid_statuses = set(df["order_status"].dropna().unique()) - valid_statuses

    print(f"Invalid order statuses: {len(invalid_statuses)}")

    if invalid_statuses:
        print(f"FAIL: Invalid statuses found: {invalid_statuses}")
        validation_passed = False
    else:
        print("PASS: Order statuses are valid")

    # 5. Delivery days validation
    negative_delivery_days = (
        df["delivery_days"].dropna() < 0
    ).sum()

    print(f"Negative delivery days: {negative_delivery_days}")

    if negative_delivery_days > 0:
        print("FAIL: Negative delivery times found")
        validation_passed = False
    else:
        print("PASS: Delivery times are valid")

    # Final result
    print("\n===== VALIDATION RESULT =====")

    if validation_passed:
        print("VALIDATION PASSED")
        return True

    print("VALIDATION FAILED")
    return False


if __name__ == "__main__":
    validate_orders()