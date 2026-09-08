USE olist_analytics;

-- ============================================================
-- QUERY 1: Total Orders
-- ============================================================

SELECT
    COUNT(*) AS total_orders
FROM fact_orders;
-- ============================================================
-- QUERY 2: Total Revenue
-- ============================================================

SELECT
    ROUND(SUM(oi.price), 2) AS total_revenue
FROM fact_order_items oi;
-- ============================================================
-- QUERY 3: Average Order Value
-- ============================================================

SELECT
    ROUND(SUM(oi.price) / COUNT(DISTINCT oi.order_id), 2)
        AS average_order_value
FROM fact_order_items oi;
-- ============================================================
-- QUERY 4: Monthly Revenue
-- ============================================================

SELECT
    YEAR(o.purchase_timestamp) AS year,
    MONTH(o.purchase_timestamp) AS month,
    ROUND(SUM(oi.price), 2) AS monthly_revenue
FROM fact_orders o
JOIN fact_order_items oi
    ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY
    YEAR(o.purchase_timestamp),
    MONTH(o.purchase_timestamp)
ORDER BY
    year,
    month;
-- ============================================================
-- QUERY 5: Revenue by Product Category
-- ============================================================

SELECT
    COALESCE(p.product_category_name, 'unknown') AS category,
    ROUND(SUM(oi.price), 2) AS total_revenue,
    COUNT(DISTINCT oi.order_id) AS total_orders
FROM fact_order_items oi
JOIN fact_orders o
    ON oi.order_id = o.order_id
JOIN dim_product p
    ON oi.product_id = p.product_id
WHERE o.order_status = 'delivered'
GROUP BY
    p.product_category_name
ORDER BY
    total_revenue DESC;
-- ============================================================
-- QUERY 6: On-Time vs Late Deliveries
-- ============================================================

SELECT
    CASE
        WHEN is_late = 1 THEN 'Late'
        WHEN is_late = 0 THEN 'On Time'
        ELSE 'Unknown'
    END AS delivery_status,
    COUNT(*) AS total_orders
FROM fact_orders
WHERE order_status = 'delivered'
GROUP BY
    CASE
        WHEN is_late = 1 THEN 'Late'
        WHEN is_late = 0 THEN 'On Time'
        ELSE 'Unknown'
    END
ORDER BY total_orders DESC;
-- ============================================================
-- QUERY 7: Average Delivery Time by Customer State
-- ============================================================

SELECT
    c.customer_state,
    COUNT(o.order_id) AS total_orders,
    ROUND(AVG(o.delivery_days), 2) AS avg_delivery_days
FROM fact_orders o
JOIN dim_customer c
    ON o.customer_id = c.customer_id
WHERE
    o.order_status = 'delivered'
    AND o.delivery_days IS NOT NULL
GROUP BY
    c.customer_state
ORDER BY
    avg_delivery_days DESC;
-- ============================================================
-- QUERY 8: Products with Above-Average Revenue
-- ============================================================

SELECT
    p.product_id,
    p.product_category_name,
    ROUND(SUM(oi.price), 2) AS product_revenue
FROM fact_order_items oi
JOIN fact_orders o
    ON oi.order_id = o.order_id
JOIN dim_product p
    ON oi.product_id = p.product_id
WHERE o.order_status = 'delivered'
GROUP BY
    p.product_id,
    p.product_category_name
HAVING
    SUM(oi.price) > (
        SELECT AVG(product_revenue)
        FROM (
            SELECT
                oi2.product_id,
                SUM(oi2.price) AS product_revenue
            FROM fact_order_items oi2
            JOIN fact_orders o2
                ON oi2.order_id = o2.order_id
            WHERE o2.order_status = 'delivered'
            GROUP BY oi2.product_id
        ) AS product_revenues
    )
ORDER BY
    product_revenue DESC;
    -- ============================================================
-- QUERY 9: Monthly Revenue Using a CTE
-- ============================================================

WITH monthly_sales AS (
    SELECT
        YEAR(o.purchase_timestamp) AS year,
        MONTH(o.purchase_timestamp) AS month,
        SUM(oi.price) AS revenue
    FROM fact_orders o
    JOIN fact_order_items oi
        ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY
        YEAR(o.purchase_timestamp),
        MONTH(o.purchase_timestamp)
)

SELECT
    year,
    month,
    ROUND(revenue, 2) AS monthly_revenue
FROM monthly_sales
ORDER BY
    year,
    month;
-- ============================================================
-- QUERY 10: Rank Products by Revenue
-- ============================================================

WITH product_sales AS (
    SELECT
        p.product_id,
        p.product_category_name,
        SUM(oi.price) AS total_revenue
    FROM fact_order_items oi
    JOIN fact_orders o
        ON oi.order_id = o.order_id
    JOIN dim_product p
        ON oi.product_id = p.product_id
    WHERE o.order_status = 'delivered'
    GROUP BY
        p.product_id,
        p.product_category_name
),

ranked_products AS (
    SELECT
        product_id,
        product_category_name,
        total_revenue,
        RANK() OVER (
            ORDER BY total_revenue DESC
        ) AS revenue_rank
    FROM product_sales
)

SELECT
    revenue_rank,
    product_id,
    product_category_name,
    ROUND(total_revenue, 2) AS total_revenue
FROM ranked_products
WHERE revenue_rank <= 10
ORDER BY revenue_rank;
-- ============================================================
-- QUERY 11: Rank Orders for Each Customer
-- ============================================================

WITH customer_orders AS (
    SELECT
        o.customer_id,
        o.order_id,
        o.purchase_timestamp,
        ROW_NUMBER() OVER (
            PARTITION BY o.customer_id
            ORDER BY o.purchase_timestamp
        ) AS order_number
    FROM fact_orders o
)

SELECT
    customer_id,
    order_id,
    purchase_timestamp,
    order_number
FROM customer_orders
WHERE order_number <= 3
ORDER BY
    customer_id,
    order_number;
-- ============================================================
-- QUERY 12: Overall E-commerce KPIs
-- ============================================================

SELECT
    COUNT(DISTINCT o.order_id) AS total_orders,

    COUNT(DISTINCT
        CASE
            WHEN o.order_status = 'delivered'
            THEN o.order_id
        END
    ) AS delivered_orders,

    ROUND(SUM(
        CASE
            WHEN o.order_status = 'delivered'
            THEN oi.price
            ELSE 0
        END
    ), 2) AS total_revenue,

    ROUND(AVG(
        CASE
            WHEN o.order_status = 'delivered'
            THEN oi.price
        END
    ), 2) AS avg_item_price,

    ROUND(AVG(
        CASE
            WHEN o.order_status = 'delivered'
            THEN o.delivery_days
        END
    ), 2) AS avg_delivery_days

FROM fact_orders o
LEFT JOIN fact_order_items oi
    ON o.order_id = oi.order_id;
-- ============================================================
-- QUERY 13: Customer Satisfaction by State
-- ============================================================

SELECT
    c.customer_state,
    COUNT(DISTINCT r.review_id) AS total_reviews,

    ROUND(
        AVG(r.review_score),
        2
    ) AS average_review_score,

    SUM(
        CASE
            WHEN r.review_score >= 4 THEN 1
            ELSE 0
        END
    ) AS positive_reviews,

    SUM(
        CASE
            WHEN r.review_score <= 2 THEN 1
            ELSE 0
        END
    ) AS negative_reviews

FROM fact_reviews r

JOIN fact_orders o
    ON r.order_id = o.order_id

JOIN dim_customer c
    ON o.customer_id = c.customer_id

GROUP BY
    c.customer_state

ORDER BY
    average_review_score DESC;
-- ============================================================
-- QUERY 14: Rank Customers by Revenue
-- ============================================================

WITH customer_revenue AS (
    SELECT
        o.customer_id,
        c.customer_city,
        c.customer_state,
        ROUND(SUM(oi.price), 2) AS total_revenue
    FROM fact_orders o
    JOIN fact_order_items oi
        ON o.order_id = oi.order_id
    JOIN dim_customer c
        ON o.customer_id = c.customer_id
    WHERE o.order_status = 'delivered'
    GROUP BY
        o.customer_id,
        c.customer_city,
        c.customer_state
),

ranked_customers AS (
    SELECT
        customer_id,
        customer_city,
        customer_state,
        total_revenue,
        RANK() OVER (
            ORDER BY total_revenue DESC
        ) AS revenue_rank
    FROM customer_revenue
)

SELECT
    revenue_rank,
    customer_id,
    customer_city,
    customer_state,
    total_revenue
FROM ranked_customers
WHERE revenue_rank <= 10
ORDER BY revenue_rank;
-- ============================================================
-- QUERY 15: Seller Performance
-- ============================================================

SELECT
    s.seller_id,
    s.seller_city,
    s.seller_state,

    COUNT(DISTINCT oi.order_id) AS total_orders,

    ROUND(SUM(oi.price), 2) AS total_revenue,

    ROUND(
        SUM(oi.price) / COUNT(DISTINCT oi.order_id),
        2
    ) AS average_order_value,

    ROUND(
        AVG(oi.price),
        2
    ) AS average_item_price

FROM fact_order_items oi

JOIN fact_orders o
    ON oi.order_id = o.order_id

JOIN dim_seller s
    ON oi.seller_id = s.seller_id

WHERE o.order_status = 'delivered'

GROUP BY
    s.seller_id,
    s.seller_city,
    s.seller_state

ORDER BY
    total_revenue DESC;
-- 16. Monthly sales performance

SELECT
    DATE_FORMAT(o.purchase_timestamp, '%Y-%m') AS month,
    COUNT(DISTINCT o.order_id) AS total_orders,
    ROUND(SUM(oi.price), 2) AS revenue,
    ROUND(SUM(oi.price) / COUNT(DISTINCT o.order_id), 2) AS avg_order_value
FROM fact_orders o
JOIN fact_order_items oi
    ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY DATE_FORMAT(o.purchase_timestamp, '%Y-%m')
ORDER BY month;
-- 17. Top 10 product categories by revenue

SELECT
    COALESCE(p.product_category_name, 'unknown') AS category,
    ROUND(SUM(oi.price), 2) AS revenue,
    COUNT(DISTINCT oi.order_id) AS orders
FROM fact_order_items oi
JOIN fact_orders o
    ON oi.order_id = o.order_id
JOIN dim_product p
    ON oi.product_id = p.product_id
WHERE o.order_status = 'delivered'
GROUP BY p.product_category_name
ORDER BY revenue DESC
LIMIT 10;
-- 18. Delivery performance

SELECT
    CASE
        WHEN o.is_late = 1 THEN 'Late'
        WHEN o.is_late = 0 THEN 'On Time'
        ELSE 'Unknown'
    END AS delivery_status,
    COUNT(*) AS total_orders,
    ROUND(
        COUNT(*) * 100.0 /
        SUM(COUNT(*)) OVER (),
        2
    ) AS percentage
FROM fact_orders o
WHERE o.order_status = 'delivered'
GROUP BY
    CASE
        WHEN o.is_late = 1 THEN 'Late'
        WHEN o.is_late = 0 THEN 'On Time'
        ELSE 'Unknown'
    END;
-- Dashboard KPI Metrics

SELECT
    COUNT(DISTINCT o.order_id) AS total_orders,

    COUNT(
        DISTINCT CASE
            WHEN o.order_status = 'delivered'
            THEN o.order_id
        END
    ) AS delivered_orders,

    ROUND(
        SUM(
            CASE
                WHEN o.order_status = 'delivered'
                THEN oi.price
                ELSE 0
            END
        ),
        2
    ) AS total_revenue,

    ROUND(
        SUM(
            CASE
                WHEN o.order_status = 'delivered'
                THEN oi.price
                ELSE 0
            END
        )
        / COUNT(
            DISTINCT CASE
                WHEN o.order_status = 'delivered'
                THEN o.order_id
            END
        ),
        2
    ) AS average_order_value,

    ROUND(
        AVG(
            CASE
                WHEN o.order_status = 'delivered'
                THEN o.delivery_days
            END
        ),
        2
    ) AS average_delivery_days

FROM fact_orders o
JOIN fact_order_items oi
    ON o.order_id = oi.order_id;