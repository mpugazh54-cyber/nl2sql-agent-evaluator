# Sales Data Agent: Data Instructions (SOTA)

This document provides the foundational data architecture, column definitions, and business logic mapping for the Sales Data Agent.

## 1. Data Source Overview
The system utilizes two primary fact tables with **monthly aggregated data**. All queries should default to the most intuitive JOIN or FILTER structure without unnecessary complexity.

| Table Name | Schema | Semantic Purpose |
| :--- | :--- | :--- |
| `fact_monthly_sales_poa_billing` | `ods.` | **Billing (Actuals)**: Revenue, shipments, billed sales, and costs. **(NO BUDGET COLUMNS)** |
| `fact_monthly_sales_poa_booking` | `ods.` | **Booking (Pipeline)**: Sales orders received, forward-looking demand. |
| `fact_monthly_sales_poa_budget` | `ods.` | **Budget (Target)**: Financial targets. **GRAIN: Customer/Region/Product.** |

---

## 2. Table Selection & Logic Protocols
### 2.1 The "Billing-First" Rule
- **DEFAULT**: Always use `ods.fact_monthly_sales_poa_billing` for all general "POA", "Sales", or "Growth" queries.
- **EXCEPTION**: Use `ods.fact_monthly_sales_poa_booking` **ONLY** if the word "Booking" or "BOOK" is explicitly mentioned in the question.

### 2.2 Order Type Filtering
- **Standard Billing**: For any billing query not involving OTR or Backlog, use `WHERE order_type = 'SHIPMENT'`.
- **OTR (Order-to-Revenue)**: **CRITICAL**: "OTR" means **ALL** `order_type` values. Do NOT filter by `order_type`. Include EVERYTHING (Shipment, Backlog, etc.).
- **Backlog Definition**: Defined as `order_type <> 'SHIPMENT'` within the **Billing** table. **Never use the Booking table for Backlog.**
- **Budget Join Rule**: NEVER join on `order_type` when querying `ods.fact_monthly_sales_poa_budget`. The budget table does not contain valid `order_type` mapping for Billing types. Join only on `year_month`, `ru`, `customer_parent`, etc.

### 2.3 Budget Alignment Protocol (CRITICAL)
### 2.3 Budget Alignment Protocol
-   **Granularity**: Budget is defined down to `customer_parent`, `pbg`, `pbu`, `local_assembler`, and `final_customer`.
-   **Mapping**: Budget uses `sub_unit_cbr` instead of `sub_unit`. Join on `budget.sub_unit_cbr = billing.sub_unit`.
-   **Aggregate-First**: For queries at Region/PBG level, aggregate Billing first. For Customer level, direct join is allowed.
-   **Data Constraint**: Budget data is only available from **2025 onwards**. Queries for 2024 budget or earlier will return 0 or NULL for budget metrics. Inform the user if they ask for pre-2025 budget.

### 2.4 Anti-Hallucination Protocol (STRICT)
- **Billing Table Limitations**: The table `ods.fact_monthly_sales_poa_billing` **DOES NOT CONTAIN** `total_budget`.
- **Budget Rule**: You **MUST** join `ods.fact_monthly_sales_poa_budget` to get any budget data.
- **FAILURE CONDITION**: Any query that attempts to select `total_budget` from `ods.fact_monthly_sales_poa_billing` is a **CRITICAL HALLUCINATION** and will fail.


---

## 3. Data Dictionary (Schema & Values)

### 3.1 Dimensions
| Column Name | Category | Description / Constraints | Sample Values (Non-Exhaustive) |
| :--- | :--- | :--- | :--- |
| `year_month` | Time | Primary temporal filter (Format: `YYYY-MM`). | `2024-12`, `2025-01` |
| `order_type` | Business | Filter Billing/Booking status. | `SHIPMENT`, `PAST DUE`, `BACKLOG`, `BOOKING` |

| `ru` | Region | Reporting Unit (Main region). | `AMERICAS`, `EMEA`, `GREAT CHINA`, `SOUTHEAST ASIA` |
| `pbg` | Product | Product Business Group (Top level). | `Capacitor`, `Resistors`, `Magnetics`, `SENSOR` |
| `pbu` | Product | Product Business Unit (Sub-type). | `MLCC`, `TANTALUM`, `R-Chip`, `Wireless` |
| `pbu_1` | Product | Product hierarchy level 1. | `COMMODITY`, `HIGH CAP` |
| `pbu_2` | Product | Product hierarchy level 2. | `Ceramic`, `METAL` |
| `local_assembler` | Customer | Secondary customer view (Assembler). | `FLEX`, `HON HAI` |
| `final_customer` | Customer | End-user customer view. | `APPLE`, `TESLA` |
| `g7` | Channel | Channel / Distributor details. | `AVNET`, `Non-G7` |
| `focus_flag`| Tracking | Indicator for focus products. | `Yes`, `No`, `Adjustment` |
| `customer_parent`| Customer | Primary customer (Invoiced). | `HON HAI`, `VALEO`, `GOOGLE`, `INFINEON` |
| `g7_flag` | Tracking | G7 Country indicator (Renamed from fu_g7_flag). | `Yes`, `No` |
| `total_sales` | Metric | Financial value (USD). | `12345.67` |
| `total_qty` | Metric | Product volume (Units). | `5000` |
| `total_cost` | Metric | Cost of goods (Only for `SHIPMENT`).| `8000` |
| `total_budget` | Metric | Budget Target (USD). Available in Budget Table ONLY. | `50000.00` |

> [!NOTE]
> **Generalization Rule**: The sample values above are representative but not exhaustive. If a user asks for a value NOT in this list (e.g., a specific customer name or a different brand), the Agent **MUST** still attempt to query it using the correct column. Do NOT assume a value is "invalid" just because it's missing from the sample list.

### 3.3 Triple-Net Entity Resolution Protocol (SOTA)
**Strategy**: (1) LLM Intelligence -> (2) Pareto List -> (3) SQL Fallback.

#### Protocol Steps
1.  **Net 1: Internal Knowledge (LLM)**
    -   Use your pre-trained knowledge to correct obvious industry typos *before* generating SQL.
    -   **Example**: User types "Compel" -> You know it's "COMPAL" -> Generate SQL for `COMPAL`.
    -   **Example**: User types "Foxcon" -> You know it's "FOXCONN".

2.  **Net 2: Pareto Reference Lists (Top 20)**
    -   Check the "Top Reference Lists" below. If exact match found, use `=`,
    -   **Example**: `ru = 'GREAT CHINA'`.

3.  **Net 3: SQL Fallback (SOUNDEX + Wildcard)**
    -   **Condition**: If the entity is NOT in the reference list AND you are not 100% sure of the correction.
    -   **Action**: You **MUST** use a performance-optimized fuzzy search combining `LIKE` and `SOUNDEX`.
    -   **Pattern**: `WHERE (col LIKE '%Input%' OR SOUNDEX(col) = SOUNDEX('Input'))`
    -   *Why?* `SOUNDEX` is faster than `DIFFERENCE` and catches phonetic typos (e.g. "Simens" matches "Siemens").

#### A. Global Synonyms & Mappings
| User Input / Synonym | Correct SQL Logic (Target Values) |
| :--- | :--- |
| **"GREATER CHINA"**, "G. China", "GC" | `ru = 'GREAT CHINA'` |
| **"SE ASIA"**, "ASEAN" | `ru = 'SOUTHEAST ASIA'` |
| **"N. AMERICA"**, "North America" | `ru = 'AMERICAS'` (unless sub-region specified) |
| **"Japan and Korea"**, "JP/KR", "Japan & Korea" | `ru = 'JAPAN & KOREA'` |
| **"APAC"**, "Asia Pacific" | `ru IN ('SOUTHEAST ASIA', 'GREAT CHINA', 'JAPAN & KOREA')`|
| **"TMSS"** | `pbu = 'Telemecanique'` |
| **"GEMS"** | `fu_global_ems_flag = 'Yes'` (Global EMS) |

#### B. Top Reference Lists (Pareto - Not Exhaustive)
> **Note**: These lists contain only the Top ~20% most frequent entities. If a user asks for something not here, trigger **Net 3 (SQL Fallback)**.

**1. Reporting Units (ru)**
`AMERICAS`, `EMEA`, `GREAT CHINA`, `JAPAN & KOREA`, `OTHERS`, `SOUTHEAST ASIA`

**2. Product Hierarchy (PBG)**
`Capacitor`, `Magnetics`, `Resistors`, `SENSOR`, `OTHER`

**3. Regional Sub-Units (sub_unit)**
`AMERICAS`, `CENTRAL EUROPE`, `CHINA`, `DIRECT FACTORY`, `EMEA`, `EMEA GLOBAL OEMS`, `INDIA`, `JAPAN`, `JAPANESE OEMS`, `KOE`, `KOREA`, `MALAYSIA`, `NORTH EUROPE`, `OTHERS`, `Out of SE Asia`, `PHIL/INDO`, `RU HEAD OFFICE`, `SE ASIA-G7`, `SINGAPORE/OEMS`, `SOUTH EUROPE`, `SOUTHEAST ASIA`, `TAIWAN`, `THAILAND`, `VIETNAM`, `WEST EUROPE & HIGH RELIABILITY`

**4. Order Types**
`SHIPMENT`, `BACKLOG`, `PAST DUE`, `CONSIGNMENT`, `BOOKING`

**6. Channels & Distributors**
- **`g7` (Distributor Name)**: `AVNET`, `ARROW`, `FUTURE`, `MOUSER`, `RUTRONIK`, `TTI`, `DIGIKEY`. *Note: This column contains the NAME, not a flag.*
- **`g7_flag` (Is Distributor)**: `Yes` (Distributor), `No` (Direct). *Values are 'Yes'/'No'. NEVER use 'Y'/'N'.*

**7. Common Customers (Excerpts)**
`ABB`, `APPLE`, `BOSCH`, `BYD`, `CISCO`, `DELL`, `DELTA`, `DENSO`, `DIGIKEY`, `FOXCONN`, `GE`, `GOOGLE`, `HUAWEI`, `INFINEON`, `INTEL`, `JABIL`, `LG`, `MICROSOFT`, `NVIDIA`, `PANASONIC`, `SAMSUNG`, `SIEMENS`, `SONY`, `TESLA`, `XIAOMI`, `ZTE`

**8. Product Detail (pbu) (Excerpts)**
`CPT`, `Ceramic`, `MLCC`, `R-Chip`, `TANTALUM`, `Teapo`, `Telemecanique`, `Wireless`, `XSEMI`

**9. Product Detail (pbu_1) (Excerpts)**
`AUTOMOTIVE`, `COMMODITY`, `HIGH CAP`, `LYTICS`, `POWER`, `SMD`, `SPECIALTY`, `Wireless`

**10. Product Detail (pbu_2) (Excerpts)**
`AC`, `AF`, `AT`, `Ceramic`, `Ferrite`, `METAL`, `Power`, `RT`, `YC`

> [!IMPORTANT]
> **Resolution Protocol**:
> 1. **Check Synonyms**: If input matches "User Input" in Table A, apply "Correct SQL Logic".
> 2. **Check Valid Lists**: If input resembles a value in List B, map to that valid value.
> 3. **Search**: If it's a specific Customer or Product Sub-unit (pbu) not listed here, use `LIKE` across relevant columns (`customer_parent`, `pbu`, etc.).

---

## 4. Business Ratios & Formulas (KISS Protocol)
Follow these simplified patterns for consistency.

### 4.1 Atomical Logic
- **Gross Profit (GP)**: `total_sales - total_cost`
- **Gross Margin % (GM%)**: `(total_sales - total_cost) / NULLIF(total_sales, 0)`
- **Average Price (ASP)**: `total_sales / NULLIF(total_qty, 0)`

### 4.2 Cross-Period Comparisons (MoM/QoQ/YoY)
Use simple CTEs to isolate periods before joining. Use `NULLIF` for all division.
- **Example MoM**: `(Curr - Prior) / NULLIF(Prior, 0)`

### 4.3 Cross-Table Aggregation Patterns (Budget vs Billing / BB Ratios)
**SOTA CTE-First Protocol**: For ANY query involving multiple fact tables (e.g., Hit Rate, Book-to-Bill), you **MUST** follow this 5-step strict isolation pattern.

1.  **Isolation (CTE 1)**: Filter & Aggregate Table A (e.g., Billing) in its own CTE.
2.  **Isolation (CTE 2)**: Filter & Aggregate Table B (e.g., Budget) in its own CTE.
3.  **Robust Join**: Use `FULL OUTER JOIN` on common keys (e.g., `ru`, `customer_parent`, `year_month`).
    *   *Why?* captures "Sales without Budget" (Upside) and "Budget without Sales" (Zero Hit Rate).
4.  **Resolution (Coalesce)**:
    *   Dimensions: `COALESCE(b.ru, t.ru) as ru`
    *   Metrics: `COALESCE(b.total_sales, 0) as actuals`, `COALESCE(t.total_budget, 0) as budget`
5.  **Calculation**: Perform final division or ratio math in the outer SELECT.

**Standard Formulas (Apply Protocol Above)**:
- **BB Ratio (Value)**: `BookingTotalSales / NULLIF(BillingTotalSales, 0)`
- **BB Qty Ratio (Volume)**: `BookingTotalQty / NULLIF(BillingTotalQty, 0)`
- **Budget Achievement % (Hit Rate %)**: `BillingTotalSales / NULLIF(BudgetTotal, 0)`
    - *NOTE*: Use `order_type='SHIPMENT'` for Billing unless "OTR" Hit Rate is asked.
    - *NOTE*: Do NOT join on `order_type` for the Budget CTE.

**Example: Hit Rate Logic**
```sql
WITH CTE_Billing AS (
    SELECT customer_parent, SUM(total_sales) as sales
    FROM ods.fact_monthly_sales_poa_billing
    WHERE order_type = 'SHIPMENT' AND -- filters...
    GROUP BY customer_parent
),
CTE_Budget AS (
    SELECT customer_parent, SUM(total_budget) as budget
    FROM ods.fact_monthly_sales_poa_budget
    WHERE -- filters...
    GROUP BY customer_parent
)
SELECT
    COALESCE(b.customer_parent, t.customer_parent) as customer_parent,
    COALESCE(b.sales, 0) as actuals,
    COALESCE(t.budget, 0) as target,
    COALESCE(b.sales, 0) / NULLIF(COALESCE(t.budget, 0), 0) as hit_rate
FROM CTE_Billing b
FULL OUTER JOIN CTE_Budget t ON b.customer_parent = t.customer_parent
```

**Example: Hit Rate MoM (Complex)**
*DO NOT try to select budget from the billing table.*
```sql
WITH Billing_Curr AS (SELECT SUM(total_sales) s FROM ods.fact_monthly_sales_poa_billing WHERE year_month='2025-02'),
     Budget_Curr  AS (SELECT SUM(total_budget) b FROM ods.fact_monthly_sales_poa_budget  WHERE year_month='2025-02'),
     Billing_Prev AS (SELECT SUM(total_sales) s FROM ods.fact_monthly_sales_poa_billing WHERE year_month='2025-01'),
     Budget_Prev  AS (SELECT SUM(total_budget) b FROM ods.fact_monthly_sales_poa_budget  WHERE year_month='2025-01')
SELECT ... 
-- Join logic in outer query
```

---

## 5. Constraints & Limitations
- **No Order Grain**: The database does NOT store individual order numbers or counts.
- **Explicit Dimensions**: DIMENSIONS (like `ru`) should only be added to `GROUP BY` if explicitly asked. Do NOT hallucinate extra breakdowns.
- **Cost Integrity**: Costs are only valid for `'SHIPMENT'`. OTR cost equals Shipment cost.

## 6. Magic Entity Logic (Semantic Layer)

> [!CAUTION]
> **CRITICAL: These mappings are MANDATORY. Failure to follow them is a FATAL ERROR.**
> - You MUST use the EXACT SQL patterns below when these terms appear in a query.
> - You MUST NOT use ILIKE or fuzzy matching for these terms.
> - VIOLATION = Agent Failure. There are NO exceptions.

### 6.1 Strategic Proxies - REQUIRED SQL MAPPINGS

| Magic Word | REQUIRED SQL Filter | FORBIDDEN Patterns |
|------------|---------------------|-------------------|
| **"AI Proxy"** | `pbu = 'TANTALUM' OR pbu_1 IN ('HIGH CAP', 'POWER')` | `LIKE '%AI%'`, `LIKE '%proxy%'` |
| **"AI Premium"** | `pbu = 'TANTALUM' OR pbu_1 IN ('HIGH CAP', 'POWER')` | `LIKE '%AI%'`, `pbg LIKE '%AI%'` |
| **"Sensor Synergy"** | `pbg = 'SENSOR'` | `LIKE '%sensor%'`, `pbu LIKE '%sensor%'` |
| **"Automotive Grade"** | `pbu_1 = 'AUTOMOTIVE'` | `LIKE '%auto%'`, `pbg LIKE '%automotive%'` |
| **"Channel Control"** | `g7_flag = 'Yes'` vs `g7_flag = 'No'` | `erp_sales_rep LIKE '%socket%'` |
| **"Socket Ownership"** | Same as Channel Control: `g7_flag` split | `LIKE '%socket%'` |
| **"G7 Distributor"** | `g7_flag = 'Yes'` | `g7_flag = 'Y'`, `g7_flag = 1` | |

> [!IMPORTANT]
> **String Values Required**: `g7_flag` values are `'Yes'` and `'No'` (STRING). NEVER use `'Y'/'N'` or `1/0`.

### 6.2 Time Period Rules - CRITICAL

| Situation | REQUIRED SQL Pattern |
|-----------|---------------------|
| "Last N months" | `year_month >= FORMAT(DATEADD(MONTH, -(N+1), GETDATE()), 'yyyy-MM') AND year_month < FORMAT(GETDATE(), 'yyyy-MM')` |
| "Latest closed month" | `year_month = FORMAT(DATEADD(MONTH, -1, GETDATE()), 'yyyy-MM')` |
| "Health Check MoM" | Compare `DATEADD(MONTH, -1, GETDATE())` vs `DATEADD(MONTH, -2, GETDATE())` |

> [!WARNING]
> **NEVER include the current month** (Feb 2026 = partial) in trend analysis unless user explicitly says "MTD" or "Current Month".

### 6.3 Risk Definitions
- **"Zombie Backlog"**: `order_type <> 'SHIPMENT' AND DATEDIFF(day, CAST(year_month + '-01' AS DATE), GETDATE()) > 90`
  - *SQL Tip*: `year_month` is a string (YYYY-MM). You MUST cast it to DATE (append '-01') for `DATEDIFF`.
- **"Pas Due Risk" / "Broken Promises"**: `order_type = 'PAST DUE'` (Show top customers by value).
- **"Profit Dilution"**: Significant Month-over-Month decline in Gross Margin % (`gm_percent`).
- **"Pricing Power"**: Rising `ASP` trend alongside rising or stable `total_qty`.
- **"Focus Products" / "Focus Tracker"**: `focus_flag = 'Yes'`. (Strict String).
- **"Key Account Churn"**: Compare Current Month Sales vs Previous Month Sales per Customer. Order by biggest decline (Value).

