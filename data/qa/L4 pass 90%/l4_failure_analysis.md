# QA Level 4 (Ratios) 失敗分析報告 (Failure Analysis Report)

**日期**: 2026-02-02  
**來源檔案**: `data/qa/step4_final_20260202_104743.csv`

## 1. 測試概況 (Overview)

| 項目 | 數值 |
| :--- | :--- |
| **總測試數 (Total Tests)** | 10 |
| **通過數 (Pass)** | 9 |
| **失敗數 (Fail)** | 1 |
| **通過率 (Pass Rate)** | **90.00%** |
| **失敗難度** | L4 (Cross-Table & Ratios) |

---

## 2. 失敗案例詳細分析 (Detailed Failure Analysis)

經過詳細檢查，唯一的失敗案例 (Row 75) 分析如下：

### Case #2: BB Ratio MoM Change (Global)
*   **問題 (Question)**: "What is the Month-over-Month percentage change in the Book-to-Bill ratio for 2024-11 versus 2024-10 across all regions?"
*   **評估結果**: **FAIL**
*   **Agent 行為**:
    *   Agent 回傳了 **按地區細分 (Regional Breakdown)** 的 MoM 變化率（針對每個地區分別計算比率變化）。
    *   Agent **未提供** 全球 (Global / All Regions) 的單一數值。
*   **失敗原因 (Evaluation Reason)**:
    *   Evaluator 指出："The agent returns MoM changes by region... instead of a single global MoM change across all regions."
    *   問題明確要求 "across all regions" (暗示聚合後的單一數值)，但 Agent 過度解讀為 "for each region"。
*   **SQL 分析**:
    *   Agent 生成的 SQL 使用了 `GROUP BY ru`，導致結果被拆分為多行。
    *   正確邏輯應移除 `GROUP BY ru`，直接計算全表的 Booking 總和與 Billing 總和，再算出全球 BB Ratio。

---

## 3. 成功案例亮點 (Success Highlights)

雖然有一例失敗，但 L4 測試整體的表現相當出色，驗證了以下能力：

1.  **跨表運算 (Cross-Table Logic)**:
    *   Agent 能正確處理 **Booking-to-Bill Ratio**，同時查詢 `fact_booking` 與 `fact_billing` 表並進行除法運算 (Case 1, 4, 9, 10)。
2.  **複雜指標 (Complex Metrics)**:
    *   正確計算 **Gross Margin % (GM%)**，公式 `(Sales - Cost) / Sales` 應用無誤 (Case 3, 6, 7)。
    *   正確計算 **YoY Growth %** (Case 8)。
3.  **算術安全 (Math Safety)**:
    *   所有涉及除法的 SQL 均使用了 `NULLIF(..., 0)`，有效防止了除以零的錯誤。
4.  **SQL 提取 (SQL Extraction)**:
    *   新的提取邏輯運作正常，成功抓取了所有案例的 SQL，之前 "SQL Missing" 的問題已解決。

---

## 4. 建議與結論 (Recommendation)

本次 L4 測試通過率達 90%，證明 Agent 已具備處理複雜比率與跨表邏輯的能力。唯獨在「聚合粒度 (Granularity)」的理解上偶有偏差（如將 "Global" 誤解為 "By Region"）。

**建議行動**:
*   這屬於輕微的語意理解偏差，可考慮在 System Prompt 中加強對 "across all regions" 或 "total" 等關鍵字的處理原則（即：若未明確要求 breakdown，則預設為聚合總數）。
*   除此之外，L4 核心邏輯驗證通過，無需對代碼進行重大修改。
