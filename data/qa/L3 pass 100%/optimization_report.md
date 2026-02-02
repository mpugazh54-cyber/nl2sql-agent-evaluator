# QA 失敗案例優化與復測報告 (Optimization Verification Report)

**日期**: 2026-02-02
**測試目標**: 針對 5 個失敗案例進行修復與驗證

## 1. 優化措施 (Optimizations)

### A. SQL 提取與缺失問題 (Missing SQL)
- **原因發現**: 
    1. **提取邏輯缺陷**: 原有的提取腳本未能捕捉到嵌入在 `<details>` 或純文本中的 SQL。
    2. **Agent 行為**: 在部分案例中，Agent 僅用自然語言描述 SQL (如 "Generated two CTEs...") 而未提供代碼，導致提取失敗。
- **修正**:
    1. **增強 `client.py`**: 重寫 SQL 提取邏輯，現在能支持多種格式 (Markdown, Text, HTML details) 的提取。
    2. **修改 Prompt (`agent_instructions.md`)**: 強制規定 Agent 在 Technical Log 中**必須**提供原始 SQL 代碼 (RAW SQL CODE)，禁止僅作文字描述。

### B. 維度/實體錯亂問題 (Dimension Mismatch)
- **用戶反饋**: Local Assembler 等實體名稱與 GT 不符不應算錯。
- **修正**: 
    - 修改 `evaluator.py`，大幅放寬 L3/L4/L5 的實體名稱比對規則。
    - **新規則**: 只要 SQL 的 `GROUP BY` 欄位正確，即便結果中的實體名稱 (Entity Names) 與 GT 不同，也視為 **PASS**。

### C. 格式調整 (Formatting)
- **修正**: 已從 `agent_instructions.md` 的輸出模板中移除 `- Data status: Month-end closed`。

---

## 2. 復測結果 (Retest Results)

在應用本地代碼修復後，對 5 個失敗案例進行了復測：

| Case | 問題 (Question) | 復測結果 | 狀態 | 說明 |
| :--- | :--- | :--- | :--- | :--- |
| **1** | BB Ratio by PBU... | **FAIL** | 待同步 | Agent 仍用文字描述 SQL ("Generated two CTEs...")，未提供代碼。需同步 Prompt 生效。 |
| **2** | Breakdown of POA BOOKED... | **PASS** | **已修復** | 增強的提取邏輯成功抓取到 300 chars SQL。 |
| **3** | POA BOOKED MoM Growth... | **FAIL** | 待同步 | Agent 仍用文字描述 SQL ("Used group-by on g7...")。需同步 Prompt 生效。 |
| **4** | Breakdown of POA BACKLOG... | **PASS** | **已修復** | 實體名稱檢查放寬，已通過。 |
| **5** | Top 5 PBU by QoQ... | **PASS** | **已修復** | 增強的提取邏輯成功抓取到 778 chars SQL。 |

**總結**: 
- **3/5 案例已通過 (Fixed)**: 證明代碼邏輯修復有效。
- **2/5 案例仍失敗**: 原因在於 Agent 尚未更新 Prompt (仍未輸出 SQL 代碼)。

---

## 3. 下一步行動 (Next Steps)

為了讓剩餘的 2 個案例通過，以及讓 "Data status" 移除生效，**必須同步指令到 Agent**。

建議執行以下指令發布更新：
```bash
python scripts/02_deploy_agent.py
```
同步後再次執行測試，預期所有案例皆能通過。
