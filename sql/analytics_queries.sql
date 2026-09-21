-- Business analytics queries for the sales_data table.
-- Column names match the cleaned SQL table created in the SQL notebook.

-- Executive KPIs
SELECT
    SUM(Sales) AS total_revenue,
    SUM(Profit) AS total_profit,
    SUM(Profit) / NULLIF(SUM(Sales), 0) AS profit_margin,
    COUNT(DISTINCT Order_ID) AS total_orders,
    SUM(Quantity) AS total_quantity,
    SUM(Sales) / NULLIF(COUNT(DISTINCT Order_ID), 0) AS average_order_value,
    COUNT(DISTINCT Customer_ID) AS unique_customers,
    AVG(Discount) AS average_discount
FROM sales_data;

-- Revenue and profitability by category
SELECT
    Category,
    SUM(Sales) AS revenue,
    SUM(Profit) AS profit,
    SUM(Profit) / NULLIF(SUM(Sales), 0) AS profit_margin,
    AVG(Discount) AS average_discount,
    SUM(Quantity) AS quantity
FROM sales_data
GROUP BY Category
ORDER BY revenue DESC;

-- Regional performance and profitability
SELECT
    Region,
    SUM(Sales) AS revenue,
    SUM(Profit) AS profit,
    SUM(Profit) / NULLIF(SUM(Sales), 0) AS profit_margin,
    COUNT(DISTINCT Order_ID) AS orders,
    SUM(Sales) / NULLIF(COUNT(DISTINCT Order_ID), 0) AS average_order_value,
    AVG(Discount) AS average_discount
FROM sales_data
GROUP BY Region
ORDER BY revenue DESC;

-- Top customers by value
SELECT
    Customer_ID,
    Customer_Name,
    SUM(Sales) AS revenue,
    SUM(Profit) AS profit,
    COUNT(DISTINCT Order_ID) AS orders,
    SUM(Sales) / NULLIF(COUNT(DISTINCT Order_ID), 0) AS average_order_value
FROM sales_data
GROUP BY Customer_ID, Customer_Name
ORDER BY revenue DESC
LIMIT 10;

-- Discount and profitability by sub-category
SELECT
    Category,
    Sub_Category,
    SUM(Sales) AS revenue,
    SUM(Profit) AS profit,
    SUM(Profit) / NULLIF(SUM(Sales), 0) AS profit_margin,
    AVG(Discount) AS average_discount,
    MAX(Discount) AS maximum_discount
FROM sales_data
GROUP BY Category, Sub_Category
ORDER BY average_discount DESC;

-- Monthly business trend
SELECT
    strftime('%Y-%m', Order_Date) AS month,
    SUM(Sales) AS revenue,
    SUM(Profit) AS profit,
    COUNT(DISTINCT Order_ID) AS orders,
    SUM(Quantity) AS quantity,
    AVG(Discount) AS average_discount
FROM sales_data
GROUP BY month
ORDER BY month;
