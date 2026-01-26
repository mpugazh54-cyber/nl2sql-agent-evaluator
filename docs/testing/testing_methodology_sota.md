# Data Agent SOTA 測試與驗證框架 (小組長方案)

為落實 IT Manager 所要求的資料準確性與透明度, 我們採用業界領先的 **"Dual-Track" (雙軌)** 驗證方法。本框架結合了「決策確定性 (Deterministic SQL)」與「語義正確性 (Semantic LLM)」。

## 1. 建立黃金資料集 (The Golden Dataset)
這是所有測試的基石。我們將針對 `valid_test_targets.csv` 進行擴增, 包含：
- **Natural Language Query**: 使用者會如何提問 (包含口語與專業術語)。
- **Ground Truth SQL**: 經由資深 DBA 審核後的標準 SQL。
- **Expected Metrics**: 預期產出的最終關鍵數據。

## 2. 雙軌驗證機制 (Dual-Track Validation)

### 軌道 A: 技術指標驗證 (Technical Accuracy)
*   **SQL 語法檢查**: 確保輸出的 SQL 語法正確, 無 Schema 找不到的問題。
*   **結果一致性 (Result Set Comparison)**: 執行 Agent 生成的 SQL 與 Golden SQL, 比較結果集。
    *   *SOTA 方法*: 使用 Pandas `assert_frame_equal` 進行數值比對, 容許誤差需設定 (如: 0.01% Rounding)。
*   **效能基準**: SQL 執行時間需低於 5 秒, 避免主管會議等待過久。

### 軌道 B: 語義與品質評分 (Semantic Quality - LLM-as-a-Judge)
使用最強模型 (如 GPT-4o 或 Claude 3.5 Sonnet) 作為「裁判」, 根據 IT Manager 的標準進行評分 (1-5 分)：
*   **溯源能力 (Traceability)**: 是否包含了正確的 Table Name 與 SQL？
*   **幻覺偵測 (Hallucination)**: Agent 是否胡謅了資料庫中不存在的欄位？
*   **解釋透明度 (Clarity)**: 計算邏輯是否易於理解？
*   **未知處理**: 當問題超出範疇時, 是否正確回答「不知道」？

## 3. 對抗性測試 (Adversarial & Edge Case Testing)
*   **Null Data Handling**: 查詢無數據的月份, 確認不會噴錯或造假。
*   **Ambiguous Joins**: 刻意使用模糊的欄位名稱, 測試 Agent 是否會詢問澄清或正確過濾。
*   **Security Injection**: 測試 Agent 是否會執行 `DROP TABLE` 等破壞性指令 (需嚴格限制資料庫 User 權限)。

## 4. 自動化回歸流水線 (CI/CD Integration)
每次 Prompt 異動或 Model 版本升級時, 自動執行完整 80% 覆蓋測試, 並產出 **Evaluation Report**。

---

## 關鍵指標目標 (KPIs)
| 指標 | 目標值 | 驗證方式 |
| :--- | :--- | :--- |
| **Accuracy (Exact Match)** | > 85% | Result Set Comparison |
| **Logic Transparency** | 100% | LLM-as-a-Judge (Prompt Checking) |
| **False Positive (Hallucination)** | 0% | Adversarial Testing |
| **"I Don't Know" Rate** | 100% Correct | Out-of-bounds Query Test |
