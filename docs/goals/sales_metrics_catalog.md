# Sales Analytics 指標百科 (Sales Metrics Catalog)

本文件匯總了所有 Sales Team 可能詢問的指標, 並依據 `billing` (實績) 與 `booking` (接單) 原始資料定義其計算邏輯。

---

## 1. 財務實績指標 (Financial Performance) - 來源: Billing
針對已出貨 (Shipment) 與實績進行分析。

| 指標名稱 (Metric) | 計算邏輯 (Logic) | 應用場景 |
| :--- | :--- | :--- |
| **Total Billing (Sales)** | `SUM(total_sales)` from Billing | 總營收達成狀況 |
| **Total Cost** | `SUM(total_cost)` from Billing | 總出貨成本 |
| **Gross Profit (GP)** | `SUM(total_sales - total_cost)` | 實際獲利金額 |
| **Gross Margin % (GM%)** | `(SUM(total_sales) - SUM(total_cost)) / SUM(total_sales)` | 獲利能力分析 |
| **Average Selling Price (ASP)** | `SUM(total_sales) / SUM(total_qty)` | 產品單價趨勢 |

## 2. 接單與需求指標 (Demand & Booking) - 來源: Booking
針對未來需求與訂單流入進行分析。

| 指標名稱 (Metric) | 計算邏輯 (Logic) | 應用場景 |
| :--- | :--- | :--- |
| **Total Bookings** | `SUM(total_sales)` from Booking | 市場需求動能 |
| **Booking Qty** | `SUM(total_qty)` from Booking | 下單顆數總量 |
| **Book-to-Bill Ratio** | `SUM(Booking total_sales) / SUM(Billing total_sales)` | 景氣領先指標 ( >1 表示需求強) |

## 3. 客戶與市場細分指標 (Segmentation & Concentration)
可應用於 Billing 與 Booking。

| 分類 (Category) | 維度 (Dimension) | 說明 (Description) |
| :--- | :--- | :--- |
| **Time** | `year_month` | YYYY-MM format timeframe |
| **Order Type** | `order_type` | Shipment, Backlog, or Booking type |
| **Product** | `brand`, `pbg`, `pbu` | Product hierarchy (Group > Unit > Brand) |
|  | `pbu_1`, `pbu_2` | Detailed product sub-units |
|  | `focus_flag` | Strategic focus product indicator (Yes/No) |
| **Region** | `ru` | Reporting Unit (Main Region) |
|  | `sub_unit` | Operational Sub-region |
| **Customer** | `customer_parent` | Bill-to Customer (Group Level) |
|  | `local_assembler` | Production/Assembly Location |
|  | `final_customer` | End User of the component |
| **Channel** | `g7` | G7 Channel Classification |
|  | `fu_us_oem_flag`, `fu_global_ems_flag` | Strategic Channel Flags (US OEM, Global EMS) |
|  | `fu_g7_flag`, `fu_emea_oem_flag` | Strategic Channel Flags (G7, EMEA OEM) |
| **Sales Rep** | `erp_sales_rep` | Assigned Sales Representative |

## 4. 進階與預警指標 (Advanced & Risk)
| 指標名稱 (Metric) | 計算邏輯 (Logic) | 應用場景 |
| :--- | :--- | :--- |
| **Past Due Analysis** | `SUM(total_sales)` where `order_type` LIKE '%PAST DUE%' | 供貨缺口或逾期未交分析 |
| **Customer Concentration** | `Sales of Top 3 / Total Sales` | 客戶集中度風險 |
| **New vs. Repeat Biz** | 比較當前月份與歷史月份的 `final_customer` 異動 | 新客戶開發績效 |

---

## 指標查詢範例 (NL to Business Logic)
*   **"這個月毛利最高的客戶是誰？"** 
    - *邏輯*: `GROUP BY customer_parent`, `ORDER BY (total_sales - total_cost) DESC`
*   **"各 Region 的 Book-to-Bill 是多少？"**
    - *邏輯*: 聯集 `billing` 與 `booking`, 按 `ru` 分組計算比例。
*   **"哪些產品線在 Great China 的銷售正在衰退？"**
    - *邏輯*: 比較 `ru = 'GREAT CHINA'` 下各 `pbg` 的 MoM 增長。
