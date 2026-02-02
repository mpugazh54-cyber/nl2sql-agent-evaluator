# QA 測試失敗原因分析報告 (Failure Analysis Report)

**日期**: 2026-02-02  
**來源檔案**: `data/qa/step4_final_20260202_091922.csv`

## 1. 測試概況 (Overview)

| 項目 | 數值 |
| :--- | :--- |
| **總測試數 (Total Tests)** | 50 |
| **通過數 (Pass)** | 45 |
| **失敗數 (Fail)** | 5 |
| **通過率 (Pass Rate)** | **90.00%** |
| **失敗難度分佈** | 所有 5 個失敗案例皆屬於 **L3 (Grouping/Aggregation)** |

---

## 2. 失敗原因分類 (Failure Categories)

經過詳細檢查，5 個失敗案例的主要原因歸納如下：

### A. SQL 未提取或缺失 (SQL Missing / Extraction Failure) - 3 例 (60%)
這是最主要的失敗原因。`generated_sql` 欄位為空 `[]`，導致無法驗證 SQL 邏輯，或 Agent 產生幻覺。

1.  **SQL 提取失敗 (Extraction Error)**:
    *   **現象**: Agent 的回答文本中包含了 SQL 語句（有 SELECT/FROM 關鍵字），但測試腳本未能成功提取。這可能是因為 SQL 未被正確包裹在 Markdown 代碼塊（Code Block）中，導致正則表達式漏抓。
    *   **案例**: *POA BOOKED MoM Growth % by g7* (Row 18)

2.  **幻覺 (Hallucination)**:
    *   **現象**: Agent 回答了具體的數字或排名，但在 Technical Log 中完全沒有 SQL 語句。這表示數據是 Agent "編造"的，而非查詢資料庫得來。
    *   **案例**: *BB Ratio by PBU* (Row 11), *Top 5 PBU by QoQ % growth* (Row 44)

### B. 維度/實體錯亂 (Dimension/Entity Mismatch) - 1 例 (20%)
*   **現象**: SQL 邏輯正確（例如正確對 `local_assembler` 分組），但在生成自然語言回答時，Agent 錯誤地將分組實體映射到了錯誤的類別（例如將 Assembler 代碼稱為 Brand 名稱）。
*   **案例**: *POA BACKLOG Qty by Local Assembler* (Row 4)

### C. 顆粒度不足 (Granularity Issue) - 1 例 (20%)
*   **現象**: 用戶要求按特定維度（如 `order_type`）細分數據，Agent 雖然 SQL 寫對了（有 Group By），但回答只給了一個總數，忽略了細分項目。
*   **案例**: *Breakdown of POA BOOKED by order type* (Row 2)

---

## 3. 詳細案例分析 (Detailed Analysis)

| Row | 難度 | 問題 (Question) | 失敗原因描述 |
| :--- | :--- | :--- | :--- |
| **11** | L3 | Show me the BB Ratio by PBU for 2024-09... | **(幻覺)** Agent 未生成 SQL，直接給出了錯誤的 PBU 列表和數值。 |
| **2** | L3 | Show me a breakdown of POA BOOKED by order type... | **(顆粒度不足)** SQL 正確分組，但回答未列出 breakdown，只給了總數 "BOOKING"。 |
| **18** | L3 | Show me the POA BOOKED MoM Growth % by g7... | **(提取失敗)** 回答文包含 SQL 關鍵字，但提取結果為空。Agent 實際上可能有做對。 |
| **4** | L3 | What is the breakdown of POA BACKLOG Qty by Local Assembler... | **(實體錯亂)** SQL 正確對 `local_assembler` 分組，但回答列出的是 Brand 名稱 (LITE-ON等)。 |
| **44** | L3 | Who are the top 5 PBU by QoQ % growth... | **(幻覺)** 未生成 SQL，直接給出了與事實不符的 Top 5 排名。 |

---

## 4. 建議改進行動 (Action Items)

1.  **修正測試腳本提取邏輯**: 
    *   針對 `generated_sql` 提取的正則表達式進行優化，以兼容未包裹在代碼塊中的 SQL 語句。這有望將 Row 18 的狀態從 Fail 轉為 Pass（若 SQL 正確）。

2.  **優化 System Prompt**:
    *   **強制 SQL 輸出**: 明確指示 Agent 必須在其思考過程或 Technical Log 中輸出 SQL，否則視為無效。
    *   **實體一致性**: 強調在回答分組問題時，必須使用查詢結果中的原始 Key 值，禁止自行"翻譯"或替換實體名稱（防止 Assembler 變 Brand）。
    *   **回答結構**: 要求 Agent 當 SQL 包含 `GROUP BY` 時，回答必須逐列列出分組結果，不可僅提供總計。

3.  **增加自我校驗 (Self-Reflection)**:
    *   引導 Agent 在回答前檢查：「我的回答中提到的實體名稱是否與 SQL 查詢結果中的一致？」。
