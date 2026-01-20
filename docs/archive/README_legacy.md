# Data Agent 專案說明

## 📁 資料夾結構

```
data_agent/
└── data_agent/
    ├── .env                           # 環境變數設定檔
    ├── fabric_data_agent_client.py    # Fabric Data Agent 客戶端
    ├── multi_agent_analyst.py         # 多代理分析系統
    └── run_analysis.py                # 執行入口程式
```

---

## 📄 各檔案說明

### 1. `.env` - 環境變數設定檔
儲存敏感配置資訊：
- **`OPENAI_API_KEY`** / **`OPENAI_BASE_URL`** / **`LLM_MODEL`** - OpenAI API 連線設定（使用 Azure OpenAI）
- **`TENANT_ID`** - Azure 租戶 ID
- **`DATA_AGENT_URL`** - Microsoft Fabric Data Agent 的 API 端點

---

### 2. `fabric_data_agent_client.py` - Fabric Data Agent 客戶端 (1249 行)
這是一個完整的 **Microsoft Fabric Data Agent** 外部呼叫客戶端，主要功能：

### 2. `fabric_data_agent_client.py` - Fabric Data Agent 客戶端
這是一個專為 **Microsoft Fabric Data Agent** 設計的外部 Python 客戶端，允許開發者從 Fabric 環境外部（如本機電腦或其他伺服器）安全地呼叫 Data Agent。

#### 核心類別說明

1.  **`TokenCache` (Token 快取管理)**
    *   **功能**: 管理 Azure AD 驗證 Token 的持久化。
    *   **運作方式**: 將取得的 Token 儲存於本地檔案 `.fabric_token_cache` 中。下次執行時會優先讀取快取，若 Token 未過期則直接使用，避免每次執行都需要重新跳出瀏覽器登入。

2.  **`FabricDataAgentClient` (主要客戶端)**
    *   **功能**: 封裝所有與 Fabric Data Agent 互動的邏輯，包含認證、連線、對話管理與結果解析。

#### 🔧 詳細運作流程 (Process Flow)

1.  **初始化與認證 (Initialization & Auth)**:
    *   程式啟動時，檢查本地是否有有效的快取 Token。
    *   若無有效 Token，呼叫 `_authenticate()` 使用 `azure.identity.InteractiveBrowserCredential` 啟動瀏覽器進行互動式登入。
    *   取得的 Token 會被快取，並用於後續所有 API 請求的 `Authorization` Header (Bearer Token)。

2.  **建立連線 (Connection)**:
    *   客戶端會建立一個經配置的 `OpenAI` client 物件，但**將 `base_url` 指向 Fabric Data Agent 的端點**，而非 OpenAI 官方 API。
    *   這使得我們可以使用標準的 OpenAI SDK 語法來操作 Fabric Data Agent。

3.  **對話執行 (Execution)**:
    *   **`ask()`**: 傳送單一問題，等待回答。
    *   **`get_run_details()`**: 這是進階分析的核心方法。
        1.  **建立 Thread**: 在 Fabric 端建立或取得一個對話串 (Thread)，確保上下文延續。
        2.  **發送訊息**: 將使用者的 Prompt 發送到該 Thread。
        3.  **監控執行 (Polling)**: 啟動 Run 並持續監控狀態 (`queued` -> `in_progress` -> `completed`)，直到 Agent 完成思考與查詢。

4.  **結果解析與 SQL 提取 (Result Parsing)**:
    *   當執行完成後，客戶端不僅取得文字回答，還會深入分析 **Run Steps**。
    *   **SQL 提取**: 透過 `_extract_sql_queries_with_data()` 方法，解析 Agent 在執行過程中產生的 Tool Calls (工具呼叫)。
    *   它會偵測 Agent 是否對 Lakehouse 執行了 SQL 查詢，並將 **SQL 語法** 與 **查詢結果預覽 (Data Preview)** 提取出來。
    *   這讓分析師不僅能看到最終答案，還能驗證 Agent 是用什麼邏輯 (SQL) 查出資料的，這是多代理分析系統能自我驗證的關鍵。

**`FabricDataAgentClient`** 核心方法：
- `_authenticate()` - 互動式瀏覽器認證
- `_refresh_token()` - Token 自動刷新
- `ask(question)` - 向 Data Agent 發問
- `get_run_details(question)` - 取得詳細執行資訊（包含 SQL 查詢）
- `get_raw_run_response()` - 取得完整原始回應
- `_extract_sql_queries_with_data()` - 提取 SQL 查詢語句

---

### 3. `multi_agent_analyst.py` - 多代理分析系統 (319 行)
實作一個 **多 Agent 協作分析框架**：

| 類別 | 功能 |
|------|------|
| **`AnalysisStep`** | 資料類別，記錄分析步驟（問題、答案、思考過程） |
| **`AnalysisContext`** | 分析上下文，儲存目標、schema 資訊、歷史步驟 |
| **`BaseAgent`** | Agent 基底類別，封裝 LLM 呼叫邏輯 |
| **`SalesManagerAgent`** | 銷售分析 Agent，負責設定目標、決定下一步驟、偵測重複模式 |
| **`Orchestrator`** | 編排器，協調 Fabric 客戶端與推理 Agent 執行分析流程 |

**工作流程**：
1. Manager Agent 根據 schema 產生分析目標
2. 循環決定下一個要問的問題
3. 透過 Fabric Data Agent 查詢資料
4. 分析回應並決定是否繼續

---

### 4. `run_analysis.py` - 執行入口程式 (45 行)
程式的**主要進入點**：
1. 載入 `.env` 環境變數
2. 初始化 `FabricDataAgentClient`（連接 Microsoft Fabric）
3. 初始化 `OpenAI` 客戶端（用於推理 Agent）
4. 建立 `Orchestrator` 並執行自動分析
5. 輸出最終分析摘要

---

## 🔄 整體架構

```
                    ┌─────────────────┐
                    │  run_analysis   │  ← 進入點
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   Orchestrator  │  ← 協調者
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
┌─────────────────┐  ┌──────────────┐  ┌────────────────┐
│ SalesManager    │  │   OpenAI     │  │  Fabric Data   │
│    Agent        │  │   Client     │  │  Agent Client  │
│ (決策/規劃)     │  │  (LLM推理)   │  │  (資料查詢)    │
└─────────────────┘  └──────────────┘  └────────────────┘
```

這是一個**自主式資料分析系統**，結合 Microsoft Fabric 的資料查詢能力與 LLM 的推理能力，自動進行銷售數據分析！

---

## 🚀 使用方式

1. 設定 `.env` 檔案中的環境變數
2. 安裝相依套件：
   ```bash
   pip install azure-identity openai python-dotenv
   ```
3. 執行分析：
   ```bash
   python run_analysis.py
   ```
