# SOTA Golden Generator 覆蓋率報告解讀指南

> 📅 更新日期：2026-01-20  
> 📊 版本：v3.0 (Progressive Difficulty Edition)

---

## 報告總覽

覆蓋率報告是 SOTA Golden Dataset Generator 的核心指標，用於追蹤測試的完整性和成功率。以下是完整的報告解讀：

```
📊 COVERAGE REPORT
============================================================

📁 Views:      10/10 (100.0%)
📏 Metrics:    8/9 (88.9%)
🔤 Dimensions: 6/9 (66.7%)
📝 Templates:  12/52 (23.1%)

📈 By Difficulty:
   L1 Foundational      [░░░░░░░░░░]   0 tested,   0.0% success
   L2 Intermediate      [░░░░░░░░░░]   0 tested,   0.0% success
   L3 Advanced          [███████░░░] 242 tested,  79.3% success
   L4 Expert            [░░░░░░░░░░]   0 tested,   0.0% success

🎯 Overall: 192/242 (79.3%)
```

---

## 各指標詳細說明

### 📁 Views（視圖覆蓋率）

**定義**：測試是否涵蓋了 Fabric 資料庫中的所有視圖。

| 指標 | 說明 |
|------|------|
| `10/10 (100.0%)` | 已測試 10 個視圖中的 10 個 |
| `Missing: view_mbr_brand...` | 尚未測試的視圖列表 |

**可用視圖清單**：
1. `view_mbr_executive` - 公司層級總覽
2. `view_mbr_regional` - 區域分析
3. `view_mbr_regional_time` - 時間序列（MoM/YoY）
4. `view_mbr_customer` - 客戶分析
5. `view_mbr_product` - 產品分析
6. `view_mbr_channel` - 通路分析
7. `view_mbr_backlog` - 訂單積壓
8. `view_mbr_brand` - 品牌分析
9. `view_mbr_tariff_premium` - 關稅分析
10. `view_mbr_ai_customer` - AI 客戶分析

**目標**：100% 覆蓋率，確保每個視圖至少被測試一次。

---

### 📏 Metrics（指標覆蓋率）

**定義**：測試是否涵蓋了所有關鍵業務指標。

| 指標 | 說明 |
|------|------|
| `8/9 (88.9%)` | 已測試 9 個指標中的 8 個 |

**可用指標清單**：
- `revenue` - 營收
- `bookings` - 訂單量
- `gross_margin_pct` - 毛利率
- `gross_margin_dollars` - 毛利金額
- `backlog_value` - 積壓訂單金額
- `plan_revenue` - 計畫營收
- `bb_ratio` - Book-to-Bill 比率
- `asp` - 平均銷售價格
- `qty` - 數量

**目標**：100% 覆蓋率，確保所有業務指標都被驗證。

---

### 🔤 Dimensions（維度覆蓋率）

**定義**：測試是否涵蓋了所有分析維度。

| 指標 | 說明 |
|------|------|
| `6/9 (66.7%)` | 已測試 9 個維度中的 6 個 |

**可用維度清單**：
- `year_month` - 時間維度
- `ru` - 區域（Region Unit）
- `customer_parent` - 客戶
- `channel` - 通路
- `pbg` - 產品群組
- `brand` - 品牌
- `age_bucket` - 帳齡
- `tariff_category` - 關稅類別
- `customer_tier` - 客戶層級

**目標**：≥80% 覆蓋率，確保主要維度都被測試。

---

### 📝 Templates（模板覆蓋率）

**定義**：測試覆蓋了多少預定義的問題模板。

| 指標 | 說明 |
|------|------|
| `12/52 (23.1%)` | 已使用 52 個模板中的 12 個 |

**模板分佈**：
- L1 Foundational：15 個模板
- L2 Intermediate：15 個模板
- L3 Advanced：12 個模板
- L4 Expert：10 個模板

**目標**：≥50% 覆蓋率，確保多樣化的問題類型被測試。

---

## 📈 難度層級分析

### 四層難度架構

| 層級 | 名稱 | 複雜度 | SQL 特性 |
|------|------|--------|----------|
| **L1** | Foundational | 1 | 單表查詢、簡單過濾、基本聚合 |
| **L2** | Intermediate | 2-3 | 多條件過濾、GROUP BY、時間範圍 |
| **L3** | Advanced | 4-5 | CASE WHEN、百分比計算、多區域比較 |
| **L4** | Expert | 6+ | CTE、視窗函數、複雜趨勢分析 |

### 當前測試結果解讀

```
L1 Foundational  [░░░░░░░░░░]   0 tested,   0.0% success
L2 Intermediate  [░░░░░░░░░░]   0 tested,   0.0% success
L3 Advanced      [███████░░░] 242 tested,  79.3% success
L4 Expert        [░░░░░░░░░░]   0 tested,   0.0% success
```

**分析**：
- 目前只測試了 L3 難度（使用 `--difficulty L3` 參數）
- L3 成功率 79.3%（192/242），表示約 20% 的查詢失敗
- 進度條 `[███████░░░]` 直觀顯示成功率

**建議行動**：
1. 分析 L3 失敗案例，找出根本原因
2. 補充 L1/L2/L4 測試以獲得完整覆蓋
3. 針對低成功率的模板進行優化

---

## 🎯 Overall（總體成功率）

```
🎯 Overall: 192/242 (79.3%)
```

| 數值 | 意義 |
|------|------|
| 192 | 成功執行的查詢數量 |
| 242 | 總測試查詢數量 |
| 79.3% | 總體成功率 |

### 成功率標準

| 等級 | 成功率 | 說明 |
|------|--------|------|
| 🔴 差 | < 60% | 需要立即修復 |
| 🟡 中等 | 60-80% | 需要改進 |
| 🟢 良好 | 80-90% | 可接受 |
| 🏆 優秀 | > 90% | 目標達成 |

**當前狀態**：🟡 中等（79.3%），接近良好等級。

---

## 失敗案例分析

當成功率低於目標時，使用 Failure Analyzer 進行根本原因分析：

```powershell
# 分析最近一次運行
python tests/failure_analyzer.py --latest

# 查看建議的修復方案
python tests/failure_analyzer.py --latest --suggest-patches
```

### 常見失敗類型

| 類型 | 說明 | 修復方式 |
|------|------|----------|
| `INVALID_COLUMN` | 欄位名稱錯誤 | 更新 Prompt 中的欄位對照 |
| `MISSING_VIEW` | 視圖不存在 | 在 Fabric 中創建視圖 |
| `SYNTAX_ERROR` | SQL 語法錯誤 | 增加 SQL 範例 |
| `UNKNOWN_FUNCTION` | 函數拼寫錯誤 | 增加函數規則 |

---

## 提升覆蓋率的建議

### 1. 平衡難度分佈

```powershell
# 測試各難度層級
python tests/golden_generator.py --difficulty L1 -n 20
python tests/golden_generator.py --difficulty L2 -n 20
python tests/golden_generator.py --difficulty L3 -n 20
python tests/golden_generator.py --difficulty L4 -n 10
```

### 2. 重置覆蓋追蹤

```powershell
python tests/golden_generator.py --reset --coverage-report
```

### 3. 使用 Analyst V2（雙提示架構）

```powershell
python tests/golden_generator.py --difficulty L3 -n 20 --analyst-v2
```

---

## 檔案位置

| 檔案 | 說明 |
|------|------|
| `tests/coverage_state.json` | 覆蓋率狀態持久化 |
| `tests/logs/run_*.csv` | 每次運行的詳細日誌 |
| `tests/golden/*.csv` | 成功案例的 Golden Dataset |
| `tests/failure_analysis_report.md` | 失敗分析報告 |

---

## 總結

覆蓋率報告是評估 SQL Agent 品質的關鍵工具：

1. **視圖覆蓋**：確保所有資料來源都被測試 ✅
2. **指標覆蓋**：驗證所有業務指標的準確性
3. **維度覆蓋**：確認各分析維度的功能
4. **模板覆蓋**：測試多樣化的問題類型
5. **成功率**：目標 ≥ 90%

持續監控這些指標，並針對低覆蓋區域進行改進，可確保 SQL Agent 的穩定性和準確性。
