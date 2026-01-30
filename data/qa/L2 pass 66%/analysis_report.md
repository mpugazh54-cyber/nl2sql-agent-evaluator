# L2 測試失敗分析報告
**日期**: 2026-01-30
**來源檔案**: `data/qa/step4_final_20260130_095912.csv`
**總失敗數**: 17

## 執行摘要 (Executive Summary)
最新的 L2 驗證執行在 50 個測試案例中產生了 17 個失敗。這些失敗主要是由於 Agent 解讀的邏輯與 Ground Truth (GT) 定義之間的不一致，而非根本性的推理錯誤。

## 失敗類別 (Failure Categories)

### 1. 日期格式與邏輯衝突 (Date Format & Logic Conflicts)
*   **問題**: Agent 有時使用字串式的日期篩選 (例如 `BETWEEN '2024-01' AND '2024-03'`)，這可能與底層數據格式 (例如 `YYYYMM` vs `YYYY-MM`) 衝突，或未能對齊特定的會計行事曆定義。
*   **影響**: 3 個案例
*   **範例**: `What is the POA BILLED Qty for YAGEO in Q1 2024?`
    *   **結果**: Agent 返回了一個天文數字，可能是因為日期篩選無效 (涵蓋了過多資料列)。

### 2. 維度範圍不匹配 (Dimension Scope Mismatch - Broad vs. Specific)
*   **問題**: Agent 通常嚴格篩選單一欄位 (例如 `pbg = 'Capacitor'`)，而 Ground Truth 會檢查整個產品階層 (例如 `pbg` OR `pbu` OR `pbu_1` LIKE '%Capacitor%')。
*   **影響**: 5 個案例
*   **範例**: `What is the total sales for the Capacitor product group in 2024-03?`
    *   **結果**: 失敗。Agent 使用嚴格欄位相等；GT 使用廣泛階層搜尋。
    *   **範例 2**: `MoM total sales for MLCC`。Agent 計算出 -5.0% vs GT -5.0% (數值相符但邏輯被標記為錯誤，因篩選寬度不同)。

### 3. 分組違規 (Grouping Violation - L2 should be Filter-Only)
*   **問題**: L2 問題定義為「僅篩選」(產出單一數值)，但 Agent 偶爾會生成「分組」查詢 (L3 行為)，將結果按維度細分。
*   **影響**: 1 個案例
*   **範例**: `What is the POA BB Ratio for PBU_1 in 2024-06?`
    *   **結果**: Agent 生成了 *每個* PBU_1 的比率表，而非所有 PBU_1項目的總計比率。

### 4. 隱性篩選遺漏 (Implicit Filter Miss - Order Type)
*   **問題**: 除非另有說明，否則 Ground Truth 幾乎總是假設一般銷售問題為 `order_type = 'SHIPMENT'`。Agent 有時會錯過這個隱含預設值，查詢了所有訂單類型。
*   **影響**: 2 個案例
*   **範例**: `What is the total quantity for HON HAI in 2024-03?`
    *   **結果**: Agent 加總了所有訂單類型；GT 僅限於 'SHIPMENT'。

### 5. 計算邏輯差異 (Calculation Logic Differences - QoQ/MoM)
*   **問題**: 成長率推導方式的差異 (例如，在 GT 語境下與 Agent 語境下哪些月份構成一個季度，或公式細微差別)。
*   **影響**: 4 個案例
*   **範例**: `POA booked QoQ growth percentage for MLCC`。
    *   **結果**: Agent 計算出 27.0%，GT 預期 16.7%。

### 6. 無答案 / 空結果 (No Answer / Empty Results)
*   **問題**: 當資料應該存在時，Agent 未能生成 SQL 或返回「查無結果」。
*   **影響**: 2 個案例
*   **範例**: `Gross Profit for ATLAS in 2024-03`。Agent 聲稱無資料；GT 找到了資料 (可能是由於上述「維度範圍」問題——查詢了錯誤的 'ATLAS' 欄位)。

## 下一步建議 (Recommendations)
1.  **優化維度邏輯**: 明確指示 Agent (透過 Prompt 或 Few-Shot)，「產品群組」或「客戶」查詢應檢查 *所有* 相關階層欄位，而不僅僅是一個。
2.  **強制預設值**: 在系統 Prompt 指令中，針對「銷售」問題硬性規定 `order_type = 'SHIPMENT'` 預設值。
3.  **嚴格禁止分組**: 進一步懲罰 L2 情境中的 Group-By 操作，以防止表格輸出。
