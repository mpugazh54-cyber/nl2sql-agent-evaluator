# QA 測試失敗原因分析報告 (Step 4)

本報告針對 `data/qa/hanson/step4_final_20260203_132119.csv` 中的測試結果進行深入分析。

**測試概況：**
*   **總題數**：20 題
*   **通過 (PASS)**：11 題
*   **失敗 (FAIL)**：9 題
*   **通過率**：55% (L2-L4 混合測試)

---

## 1. 失敗核心原因分類 (Root Cause Analysis)

經過逐題分析，失敗原因主要集中在以下三類：

### A. 時間窗口與數據可用性衝突 (Time Window / Data Availability) - **最嚴重 (5 題)**
這是導致失敗的最大原因。測試數據截止於 **2025-10**，但問題詢問的是 `Nov 2025`, `Dec 2025` 或 `Q4 2025`。
*   **Agent 行為**：Agent 試圖「聰明地」調整時間範圍至「最近可用月份」(Sep/Oct)，或者包含未來月份 (Nov/Dec) 導致資料為空或與 GT (Ground Truth) 預期不符。
*   **Ground Truth (GT) 邏輯**：嚴格要求針對「可用數據窗口」或「指定的無數據月份」進行回應，Agent 的自動調整被視為不符合 User Intent。
*   **案例**：
    *   **L3 - Q4 2025 Book-to-Bill**: User 問 Q4，Agent 查了 Oct-Dec，但 GT 期望僅計算 Oct (因 Nov/Dec 無資料)。
    *   **L3 - Booking Share (Nov 2025)**: User 問 Nov，GT 期望回報「無資料/超出範圍」，但 Agent 硬算了一個結果 (即使是錯誤的)。
    *   **L4 - Brand Momentum (Nov-Dec)**: User 問 Nov-Dec，Agent 自動改為分析 Sep-Oct，被判定為「時間窗口錯誤」。

### B. 維度映射與過濾邏輯錯置 (Dimension Mapping & Filtering) - **(3 題)**
Agent 在處理特定維度時，產生了幻覺 (Hallucination) 或使用了錯誤的過濾條件。
*   **案例 1 (Channel Mapping)**：問題詢問 "Distribution channel"，但 Booking 表無此欄位。Agent 卻自創了 `focus_flag ILIKE '%dist%'` 過濾條件，導致結果錯誤。
*   **案例 2 (Customer Grouping)**：問題詢問 "Top 5 Customers"。GT 期望將 `customer_parent`, `local_assembler`, `final_customer` 進行 `COALESCE` 合併後再排名，但 Agent 僅對 `customer_parent` 進行 Group By，導致排名邏輯不完整。
*   **案例 3 (Date Filtering)**：問題要求 "2025 (Jan-Oct)"。Agent 使用 `year_month LIKE '2025%'` (含全年)，雖邏輯相似但精確度不足。

### C. 技術限制/拒絕回答 (Refusal Answer) - **(1 題)**
*   **案例 (Rolling Average)**：Agent 在計算 3-month rolling average 時，輸出 "We encountered an issue... technical limitations"，未生成 SQL。這屬於 Agent 能力限制或 Prompt 過度保守導致的拒絕回答。

---

## 2. 詳細失敗案例列表

| 難度 | 問題摘要 | 失敗主因 | 詳細說明 |
| :--- | :--- | :--- | :--- |
| **L2** | **Bookings for Distribution channel** | **幻覺過濾** | Booking 表無 Channel 欄位，Agent 卻使用 `focus_flag ILIKE '%dist%'`。正確應為不過濾或回報無法區分。 |
| **L2** | **Top 5 customers by revenue** | **分組錯誤** | 僅 Group By `customer_parent`。應考量多重 Customer 欄位 (Parent/Assembler/Final)。 |
| **L2** | **Bottom 3 products by booking** | **時間範圍** | 使用 `LIKE '2025%'` (全年)，GT 限定 `2025-01` to `2025-10`。 |
| **L3** | **Book-to-Bill ratio Q4 2025** | **時間範圍** | Agent 查 `2025-10`~`12`。因資料僅到 Oct，GT 期望僅用 Oct 代表 Q4。 |
| **L3** | **Booking Share Asia Nov 2025** | **時間/公式** | 1. 查詢無數據月份。 2. 公式錯誤 (Share 應為 Booking/Total，Agent 寫錯)。 |
| **L4** | **Customers Booking > Billing Dec 2025** | **時間範圍** | Agent 查 Dec (無資料) 或自動切換 Oct，與 GT 預期不一致。 |
| **L4** | **Brand Momentum Nov to Dec 2025** | **自作聰明** | User 問 Nov-Dec，Agent 自動分析 Sep-Oct。應明確告知無資料或照查 (回傳空值)。 |
| **L4** | **3-month rolling average** | **拒絕回答** | Agent 回報 "Technical limitation"，未生成 Window Function SQL。 |
| **L4** | **Channel Mix Comparison** | **(Pass)** | *註：此題雖標示 FAIL 但原因其實是 GT 認為需明確 Mapping，實際 Agent 邏輯尚可。* (修正：CSV 顯示此題 PASS) |

---

## 3. 建議修正行動 (Action Items)

1.  **強化「無數據」處理原則**：
    *   更新 `agent_instructions.md`：明確指示若 User 詢問「未來時間」或「無數據月份」，應**優先生成查詢並回傳空結果** (並在解釋中說明無數據)，而**不是**自動切換到有數據的月份 (這會被視為答非所問)。
2.  **修正 Customer Grouping 邏輯**：
    *   在 `agent_instructions.md` 的 Entity Resolution 章節，針對 "Top Customer" 查詢，強制要求使用 `COALESCE(customer_parent, ...)` 進行分組。
3.  **移除 Booking Channel 幻覺**：
    *   在 `data_instructions.md` 明確標註 Booking 表**不支援** Channel/Distribution 維度過濾，避免 Agent 硬湊條件。
4.  **增強 SQL Window Function 能力**：
    *   在 Few-Shot Examples 中加入 Rolling Average 的標準寫法，讓 Agent 敢於生成複雜 SQL。
