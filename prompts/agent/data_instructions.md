# Sales Data Agent: Data Instructions (SOTA)

This document provides the foundational data architecture, column definitions, and business logic mapping for the Sales Data Agent.

## 1. Data Source Overview
The system utilizes two primary fact tables with **monthly aggregated data**. All queries should default to the most intuitive JOIN or FILTER structure without unnecessary complexity.

| Table Name | Schema | Semantic Purpose |
| :--- | :--- | :--- |
| `fact_monthly_sales_poa_billing` | `ods.` | **Billing (Actuals)**: Revenue, shipments, billed sales, and costs. |
| `fact_monthly_sales_poa_booking` | `ods.` | **Booking (Pipeline)**: Sales orders received, forward-looking demand. |

---

## 2. Table Selection & Logic Protocols
### 2.1 The "Billing-First" Rule
- **DEFAULT**: Always use `ods.fact_monthly_sales_poa_billing` for all general "POA", "Sales", or "Growth" queries.
- **EXCEPTION**: Use `ods.fact_monthly_sales_poa_booking` **ONLY** if the word "Booking" or "BOOK" is explicitly mentioned in the question.

### 2.2 Order Type Filtering
- **Standard Billing**: For any billing query not involving OTR or Backlog, use `WHERE order_type = 'SHIPMENT'`.
- **OTR (Order-to-Revenue)**: Include ALL `order_type` values (Remove the 'SHIPMENT' filter).
- **Backlog Definition**: Defined as `order_type <> 'SHIPMENT'` within the **Billing** table. **Never use the Booking table for Backlog.**

---

## 3. Data Dictionary (Schema & Values)

### 3.1 Dimensions
| Column Name | Category | Description / Constraints | Sample Values (Non-Exhaustive) |
| :--- | :--- | :--- | :--- |
| `year_month` | Time | Primary temporal filter (Format: `YYYY-MM`). | `2024-12`, `2025-01` |
| `order_type` | Business | Filter Billing/Booking status. | `SHIPMENT`, `PAST DUE`, `BACKLOG`, `BOOKING` |
| `brand` | Product | Product brand names. | `YAGEO`, `PULSE`, `KEMET`, `CHILISIN`, `TOKIN` |
| `ru` | Region | Reporting Unit (Main region). | `AMERICAS`, `EMEA`, `GREAT CHINA`, `SOUTHEAST ASIA` |
| `pbg` | Product | Product Business Group (Top level). | `Capacitor`, `Resistors`, `Magnetics`, `SENSOR` |
| `pbu` | Product | Product Business Unit (Sub-type). | `MLCC`, `TANTALUM`, `R-Chip`, `Wireless` |
| `focus_flag`| Tracking | Indicator for focus products. | `Yes`, `No`, `Adjustment` |
| `customer_parent`| Customer | Primary customer (Invoiced). | `HON HAI`, `VALEO`, `GOOGLE`, `INFINEON` |
| `total_sales` | Metric | Financial value (USD). | `12345.67` |
| `total_qty` | Metric | Product volume (Units). | `5000` |
| `total_cost` | Metric | Cost of goods (Only for `SHIPMENT`).| `8000` |

> [!NOTE]
> **Generalization Rule**: The sample values above are representative but not exhaustive. If a user asks for a value NOT in this list (e.g., a specific customer name or a different brand), the Agent **MUST** still attempt to query it using the correct column. Do NOT assume a value is "invalid" just because it's missing from the sample list.

### 3.3 Authoritative Entity Resolution & Correct Lists
Use these lists to validate and map user inputs BEFORE generating SQL.

#### A. Global Synonyms & Mappings
| User Input / Synonym | Correct SQL Logic (Target Values) |
| :--- | :--- |
| **"GREATER CHINA"**, "G. China", "GC" | `ru IN ('GREAT CHINA', 'GREATER CHINA')` |
| **"SE ASIA"**, "ASEAN" | `ru = 'SOUTHEAST ASIA'` |
| **"N. AMERICA"**, "North America" | `ru = 'AMERICAS'` (unless sub-region specified) |
| **"APAC"**, "Asia Pacific" | `ru IN ('SOUTHEAST ASIA', 'GREAT CHINA', 'JAPAN & KOREA')`|
| **"TMSS"** | `brand = 'Telemecanique'` |
| **"GEMS"** | `fu_global_ems_flag = 'Y'` (Global EMS) |

#### B. Valid Value Lists (For Fuzzy Matching)
If input is not an exact match, check against these valid values:

**1. Brands**
`BOTHHAND`, `CHILISIN`, `FERROXCUBE`, `KEMET`, `Nexensos`, `PULSE`, `TOKIN`, `Telemecanique`, `YAGEO`

**2. Reporting Units (ru)**
`AMERICAS`, `EMEA`, `GREAT CHINA`, `JAPAN & KOREA`, `OTHERS`, `SOUTHEAST ASIA`

**3. Product Hierarchy (PBG)**
`Capacitor`, `Magnetics`, `Resistors`, `SENSOR`, `OTHER`

**4. Regional Sub-Units (sub_unit)**
`AMERICAS`, `CENTRAL EUROPE`, `CHINA`, `DIRECT FACTORY`, `EMEA`, `EMEA GLOBAL OEMS`, `INDIA`, `JAPAN`, `JAPANESE OEMS`, `KOE`, `KOREA`, `MALAYSIA`, `NORTH EUROPE`, `OTHERS`, `Out of SE Asia`, `PHIL/INDO`, `RU HEAD OFFICE`, `SE ASIA-G7`, `SINGAPORE/OEMS`, `SOUTH EUROPE`, `SOUTHEAST ASIA`, `TAIWAN`, `THAILAND`, `VIETNAM`, `WEST EUROPE & HIGH RELIABILITY`

**5. Order Types**
`SHIPMENT`, `BACKLOG`, `PAST DUE`, `CONSIGNMENT`, `BOOKING`

**6. Channels (g7)**
`AVNET`, `ARROW`, `FUTURE`, `MOUSER`, `RUTRONIK`, `TTI`, `DIGIKEY`, `Non-G7`

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
> 3. **Search**: If it's a specific Customer or Product Sub-unit (pbu) not listed here, use `ILIKE` across relevant columns (`customer_parent`, `pbu`, etc.).

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

### 4.3 BB Ratio Patterns
- **Aggregation Pattern**: Calculate Booking and Billing totals independently (using separate CTEs). Avoid standard `INNER JOIN` on keys.
- **BB Ratio (Value)**: `BookingTotalSales / NULLIF(BillingTotalSales, 0)`
- **BB Qty Ratio (Volume)**: `BookingTotalQty / NULLIF(BillingTotalQty, 0)`

---

## 5. Constraints & Limitations
- **No Order Grain**: The database does NOT store individual order numbers or counts.
- **Explicit Dimensions**: DIMENSIONS (like `ru` or `brand`) should only be added to `GROUP BY` if explicitly asked. Do NOT hallucinate extra breakdowns.
- **Cost Integrity**: Costs are only valid for `'SHIPMENT'`. OTR cost equals Shipment cost.
