-- Total Revenue Query

SELECT
    SUM(Sales) AS total_revenue
FROM sales_data;

-- Revenue by Category

SELECT
    Category,
    SUM(Sales) AS revenue
FROM sales_data
GROUP BY Category
ORDER BY revenue DESC;

-- Regional Performance

SELECT
    Region,
    SUM(Sales) AS total_sales,
    AVG(Sales) AS avg_order_value
FROM sales_data
GROUP BY Region
ORDER BY total_sales DESC;

-- Top 10 Customers

SELECT
    Customer_Name,
    SUM(Sales) AS customer_revenue
FROM sales_data
GROUP BY Customer_Name
ORDER BY customer_revenue DESC
LIMIT 10

-- Monthly Revenue Trend
SELECT
    -- Assumes date is like 'YYYY-MM-DD'.
    SUBSTR(Order_Date, 1, 7) AS month, 
    SUM(Sales) AS monthly_revenue
FROM sales_data
GROUP BY month
ORDER BY month