# SOTA 自動化測試流程建立手冊

要達成 `ref_測試覆蓋率.md` 所展現的專業自動化驗證, 我們需要建立一套包含「自動生成、雙軌驗證、失敗分析、覆蓋追蹤」的完整生態系。以下是建立此流程所需的組成組件與步驟。

---

## 1. 核心組件 (What to Build?)

### A. 工具與腳本 (Scripts)
1. **`golden_generator.py` (黃金資料產生器)**: 
   - 功能：整合 `sales_metrics_catalog.md` 提供的指標, 生成不同難度 (L1~L4) 的問題模板。
   - 產出：`tests/golden/qa_pairs.csv` (含 NL 問題、標準 SQL 與預期結果)。
2. **`test_runner.py` (測試執行器)**:
   - 功能：呼叫 Data Agent 獲取 SQL, 執行並與預期結果對比。
   - 產出：`tests/logs/run_YYYYMMDD.csv`。
3. **`failure_analyzer.py` (失敗分析器)**:
   - 功能：讀取運行日誌, 自動分類錯誤 (如 `INVALID_COLUMN`, `LOGIC_ERROR`)。
   - 產出：`tests/failure_analysis_report.md`。

### B. 資料結構 (Data Structure)
- `tests/coverage_state.json`: 持久化儲存「哪些指標/維度已被測試、成功率為何」。
- `tests/golden/`: 存儲已通過驗證、可作為基準的測試案例。

---

## 2. 測試流程 (The Workflow)

### 第一階段：定義與初始化 (Init)
*   **Step 1**: 將 `sales_metrics_catalog.md` 中的指標標記為待測項目。
*   **Step 2**: 初始化 `coverage_state.json`, 設定 0% 覆蓋。

### 第二階段：循環生成與測試 (Iterative Testing)
*   **Step 3 (Generate)**: 使用 `golden_generator.py` 針對每一種指標與維度組合生成測試。
    - *範例*: 針對 `Total Sales` (指標) + `RU` (維度) 生成 L2 問題。
*   **Step 4 (Run)**: 執行測試並記錄「Agent SQL」與「Execution Result」。
*   **Step 5 (Evaluate)**: 
    - **Technical**: 比對數據結果。
    - **Semantic**: 使用 `evaluator_prompt.md` 評分。

### 第三階段：分析與優化 (Analyze & Patch)
*   **Step 6 (Failure Analysis)**: 執行 `failure_analyzer.py` 找出低成功率的模板。
*   **Step 7 (Refine)**: 根據分析結果修正 Data Agent 的 System Prompt 或資料庫 Schema 映射。

### 第四階段：報告與上線准駁 (Reporting)
*   **Step 8**: 自動生成 `測試覆蓋率.md`。
*   **Step 9**: IT Manager 根據 Overall Success Rate  與 Coverage 決定是否正式 Release。

---

## 3. SOTA 關鍵成功因素
- **Golden Reference**: 必須先由「人/專家」確定標準答案 (SQL/Result), AI 才有準則可循。
- **Difficulty Grading**: 不要一次測全部, 先從 L1 (營收總計) 通過, 再測 L3 (跨表 Book-to-Bill)。
- **Idempotency**: 測試應可重複執行, 且不更動資料庫狀態。
