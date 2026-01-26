# Data Agent 準確性與上線評核標準 (IT Manager 檢核文件)

本文件定義 Data Agent 在提供給 Sales Team 及高階主管會議使用前, 必須達到的技術與品質門檻。作為 IT 主管, 我們首要關注的是**資料的可信度 (Trust)**、**準確性 (Accuracy)** 與**營運透明度 (Observability)**。

## 1. 商業與業務目標 (Business Alignment)
*   **常見問題涵蓋率**: Data Agent 必須能正確回答 80% 以上的業務常用問題 (FAQ)。
    *   *評估方式*: 透過 `valid_test_targets.csv` 進行回測, 成功率需達標。
*   **場景適用性**: 需確保在「高階主管會議」即時查詢時, 回應時間與邏輯一致。

## 2. 資料正確性與可信度 (Data Integrity & Trust)
*   **資料溯源 (Traceability)**: 所有的數據回饋必須包含資料來源 (Source Tables) 或執行的 SQL Query 代碼。
*   **計算邏輯細節 (Logic Clarity)**: 針對複雜指標 (如 YoY, Gross Margin), Agent 需主動列出計算公式或邏輯, 供人工覆核。
*   **防止幻覺 (Hallucination Prevention)**: 
    *   嚴格執行「知之為知之, 不知為不知」。若資料庫無對應欄位或數據, Agent 必須回報「不知道」, 嚴禁編造數據。
    *   Agent 輸出的數值必須與 SQL 執行結果完全一致。

## 3. 系統透明度與維護 (System Observability)
*   **日誌記錄 (Execution Logs)**: 每次對話的後台 SQL Query 必須持久化儲存, 以便進行事後審計 (Audit)。
*   **除錯能力**: 提供清晰的錯誤訊息, 當 SQL 執行失敗時, IT 人員應能快速定位是 Schema 異動還是 Prompt 解析問題。

---

## 上線前檢核表 (Pre-launch Checklist)
- [ ] 通過 80% 業務基準測試
- [ ] 輸出內容包含 SQL/來源說明
- [ ] 複雜邏輯有補充說明
- [ ] SQL Logs 追蹤機制已就緒
- [ ] 壓力測試 (主管會議多人在線情境)
