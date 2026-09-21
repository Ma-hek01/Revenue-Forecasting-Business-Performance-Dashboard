-- Core business queries for the sales_data table.

-- Total Revenue
SELECT SUM(Sales) AS total_revenue
FROM sales_data;

-- Revenue by Category
SELECT Category, SUM(Sales) AS revenue
FROM sales_data
GROUP BY Category
ORDER BY revenue DESC;

-- Regional Performance
SELECT
    Region,
    SUM(Sales) AS total_sales,
    SUM(Profit) AS total_profit,
    AVG(Sales) AS avg_line_sales,
    SUM(Sales) / NULLIF(COUNT(DISTINCT Order_ID), 0) AS average_order_value
FROM sales_data
GROUP BY Region
ORDER BY total_sales DESC;

-- Top 10 Customers
SELECT
    Customer_ID,
    Customer_Name,
    SUM(Sales) AS customer_revenue,
    SUM(Profit) AS customer_profit,
    COUNT(DISTINCT Order_ID) AS orders
FROM sales_data
GROUP BY Customer_ID, Customer_Name
ORDER BY customer_revenue DESC
LIMIT 10;

-- Monthly Revenue Trend
-- The source data stores dates as MM/DD/YYYY, so strftime is applied
-- after SQLite date parsing rather than using SUBSTR on the raw string.
SELECT
    strftime('%Y-%m', date(Order_Date)) AS month,
    SUM(Sales) AS monthly_revenue
FROM sales_data
GROUP BY month
ORDER BY month;
