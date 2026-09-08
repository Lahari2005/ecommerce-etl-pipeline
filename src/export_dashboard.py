import os
from dotenv import load_dotenv
import pandas as pd
import mysql.connector

load_dotenv()

conn = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DATABASE")
)
query = """
SELECT
    DATE_FORMAT(o.purchase_timestamp, '%Y-%m') AS month,
    o.order_id,
    o.customer_id,
    c.customer_state,
    oi.product_id,
    COALESCE(p.product_category_name, 'unknown') AS product_category,
    oi.seller_id,
    oi.price,
    oi.freight_value,
    o.order_status,
    o.delivery_days,
    CASE
        WHEN o.is_late = 1 THEN 'Late'
        WHEN o.is_late = 0 THEN 'On Time'
        ELSE 'Unknown'
    END AS delivery_status
FROM fact_orders o
JOIN fact_order_items oi
    ON o.order_id = oi.order_id
JOIN dim_customer c
    ON o.customer_id = c.customer_id
JOIN dim_product p
    ON oi.product_id = p.product_id
WHERE o.order_status = 'delivered';
"""

df = pd.read_sql(query, conn)

output_path = "data/processed/olist_dashboard.csv"
df.to_csv(output_path, index=False)

print(f"Dashboard data exported successfully!")
print(f"Rows: {len(df)}")
print(f"Saved to: {output_path}")

conn.close()