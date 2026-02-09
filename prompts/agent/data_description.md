### Sales POA (Point of Acquisition) Data Source

This authoritative data source contains detailed monthly sales performance, forward-looking demand, and financial targets for the sales organization. Use this source to answer questions about revenue, gross margin, backlog, book-to-bill ratios, and budget achievement.

**Contents & Nuances:**
-   **`fact_monthly_sales_poa_billing`**: **Realized Revenue**. Contains actual billing and cost data. Filter by `order_type = 'SHIPMENT'` for recognized revenue. Use for Sales Trends, YoY Growth, ASP, and Gross Profit analysis.
-   **`fact_monthly_sales_poa_booking`**: **Forward Demand**. Contains new orders booked. Use for Pipeline visibility, Backlog analysis (unshipped orders), and Market Demand sensing.
-   **`fact_monthly_sales_poa_budget`**: **Financial Targets**. Contains budget goals. `order_type` is typically 'BUDGET'. Join with Billing table on common dimensions (`year_month`, `ru`, `pbg`, `customer_parent`) to calculate **Hit Rate** and **Budget Achievement %**.

**Key Metrics & Dimensions:**
-   **Metrics**: `total_sales` (Revenue/Bookings), `total_qty`, `total_cost`, `total_budget`.
-   **Dimensions**: `year_month`, `ru` (Region), `pbg`/`pbu` (Product Hierarchy), `customer_parent`, `g7` (Channel Type).
