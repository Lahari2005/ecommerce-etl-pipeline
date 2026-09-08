import mysql.connector
from pathlib import Path
import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"


# ============================================================
# CONNECT TO MYSQL
# ============================================================

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Lahari143@",
    database="olist_analytics"
)

cursor = connection.cursor()

print("Connected to MySQL successfully!")


try:

    # ========================================================
    # 1. LOAD CUSTOMERS
    # ========================================================

    customers = pd.read_csv(
        RAW_DIR / "olist_customers_dataset.csv"
    )

    customer_query = """
    INSERT IGNORE INTO dim_customer (
        customer_id,
        customer_unique_id,
        customer_zip_code_prefix,
        customer_city,
        customer_state
    )
    VALUES (%s, %s, %s, %s, %s)
    """

    for _, row in customers.iterrows():

        values = tuple(
            None if pd.isna(value) else value
            for value in [
                row["customer_id"],
                row["customer_unique_id"],
                row["customer_zip_code_prefix"],
                row["customer_city"],
                row["customer_state"]
            ]
        )

        cursor.execute(customer_query, values)

    print(f"Customers loaded: {len(customers)}")


    # ========================================================
    # 2. LOAD PRODUCTS
    # ========================================================

    products = pd.read_csv(
        RAW_DIR / "olist_products_dataset.csv"
    )

    product_query = """
    INSERT IGNORE INTO dim_product (
        product_id,
        product_category_name,
        product_name_length,
        product_description_length,
        product_photos_qty,
        product_weight_g,
        product_length_cm,
        product_height_cm,
        product_width_cm
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    for _, row in products.iterrows():

        values = tuple(
            None if pd.isna(value) else value
            for value in [
                row["product_id"],
                row["product_category_name"],
                row["product_name_lenght"],
                row["product_description_lenght"],
                row["product_photos_qty"],
                row["product_weight_g"],
                row["product_length_cm"],
                row["product_height_cm"],
                row["product_width_cm"]
            ]
        )

        cursor.execute(product_query, values)

    print(f"Products loaded: {len(products)}")


    # ========================================================
    # 3. LOAD SELLERS
    # ========================================================

    sellers = pd.read_csv(
        RAW_DIR / "olist_sellers_dataset.csv"
    )

    seller_query = """
    INSERT IGNORE INTO dim_seller (
        seller_id,
        seller_zip_code_prefix,
        seller_city,
        seller_state
    )
    VALUES (%s, %s, %s, %s)
    """

    for _, row in sellers.iterrows():

        values = tuple(
            None if pd.isna(value) else value
            for value in [
                row["seller_id"],
                row["seller_zip_code_prefix"],
                row["seller_city"],
                row["seller_state"]
            ]
        )

        cursor.execute(seller_query, values)

    print(f"Sellers loaded: {len(sellers)}")


    # ========================================================
    # 4. LOAD ORDERS
    # ========================================================

    orders = pd.read_csv(
        PROCESSED_DIR / "cleaned_orders.csv"
    )

    order_query = """
    INSERT IGNORE INTO fact_orders (
        order_id,
        customer_id,
        order_status,
        purchase_timestamp,
        approved_at,
        delivered_carrier_at,
        delivered_customer_at,
        estimated_delivery_at,
        purchase_date,
        purchase_year,
        purchase_month,
        delivery_days,
        is_late
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    for _, row in orders.iterrows():

        values = tuple(
            None if pd.isna(value) else value
            for value in [
                row["order_id"],
                row["customer_id"],
                row["order_status"],
                row["order_purchase_timestamp"],
                row["order_approved_at"],
                row["order_delivered_carrier_date"],
                row["order_delivered_customer_date"],
                row["order_estimated_delivery_date"],
                row["purchase_date"],
                row["purchase_year"],
                row["purchase_month"],
                row["delivery_days"],
                row["is_late"]
            ]
        )

        cursor.execute(order_query, values)

    print(f"Orders loaded: {len(orders)}")


    # ========================================================
    # 5. LOAD ORDER ITEMS
    # ========================================================

    order_items = pd.read_csv(
        RAW_DIR / "olist_order_items_dataset.csv"
    )

    order_items_query = """
    INSERT IGNORE INTO fact_order_items (
        order_id,
        order_item_id,
        product_id,
        seller_id,
        shipping_limit_date,
        price,
        freight_value
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    for _, row in order_items.iterrows():

        values = tuple(
            None if pd.isna(value) else value
            for value in [
                row["order_id"],
                row["order_item_id"],
                row["product_id"],
                row["seller_id"],
                row["shipping_limit_date"],
                row["price"],
                row["freight_value"]
            ]
        )

        cursor.execute(order_items_query, values)

    print(f"Order items loaded: {len(order_items)}")


    # ========================================================
    # 6. LOAD PAYMENTS
    # ========================================================

    payments = pd.read_csv(
        RAW_DIR / "olist_order_payments_dataset.csv"
    )

    payment_query = """
    INSERT IGNORE INTO fact_payments (
        order_id,
        payment_sequential,
        payment_type,
        payment_installments,
        payment_value
    )
    VALUES (%s, %s, %s, %s, %s)
    """

    for _, row in payments.iterrows():

        values = tuple(
            None if pd.isna(value) else value
            for value in [
                row["order_id"],
                row["payment_sequential"],
                row["payment_type"],
                row["payment_installments"],
                row["payment_value"]
            ]
        )

        cursor.execute(payment_query, values)

    print(f"Payments loaded: {len(payments)}")


    # ========================================================
    # 7. LOAD REVIEWS
    # ========================================================

    reviews = pd.read_csv(
        RAW_DIR / "olist_order_reviews_dataset.csv"
    )

    review_query = """
    INSERT IGNORE INTO fact_reviews (
        review_id,
        order_id,
        review_score,
        review_comment_title,
        review_comment_message,
        review_creation_date,
        review_answer_timestamp
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    for _, row in reviews.iterrows():

        values = tuple(
            None if pd.isna(value) else value
            for value in [
                row["review_id"],
                row["order_id"],
                row["review_score"],
                row["review_comment_title"],
                row["review_comment_message"],
                row["review_creation_date"],
                row["review_answer_timestamp"]
            ]
        )

        cursor.execute(review_query, values)

    print(f"Reviews loaded: {len(reviews)}")


    # ========================================================
    # COMMIT
    # ========================================================

    connection.commit()

    print()
    print("========================================")
    print("DATA LOADING COMPLETED SUCCESSFULLY")
    print("========================================")


except Exception as e:

    connection.rollback()

    print()
    print("========================================")
    print("ERROR OCCURRED")
    print("========================================")
    print(e)
    print("Changes have been rolled back.")


finally:

    cursor.close()
    connection.close()

    print("MySQL connection closed.")