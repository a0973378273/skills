---
name: jira-task
description: 從 Jira issue 自動分析需求、列出 TODO 清單並依序完成任務。會主動提出需要確認的問題和缺少的資源。適合用於實作新功能、修復 bug 或任何需要完整執行的 Jira 任務。
---

# Jira 任務自動實作

自動化從 Jira issue 到完成實作的完整流程。

## 快速使用

使用 Issue Key：
```bash
/jira-task EK-907
```

使用完整 URL：
```bash
/jira-task https://showyouapp.atlassian.net/browse/EK-907
```

不提供參數（會提示輸入）：
```bash
/jira-task
```

## 執行流程

當你執行這個 skill 時，我會自動完成以下步驟：

### 1. 📋 獲取並分析 Jira Issue
- 解析提供的 Jira URL 或 Issue Key（如：EK-907）
- 使用 Jira MCP server 獲取 issue 詳細資訊
- 提取並分析：
  - Summary（標題）
  - Description（詳細描述）
  - Issue Type（類型：Bug/Story/Task 等）
  - Priority（優先級）
  - Acceptance Criteria（驗收條件，如有）
  - Comments（相關討論）
  - Attachments（附件，如設計圖等）

### 2. 🤔 需求分析與確認
- 分析需要修改的文件和功能範圍
- 識別可能需要的資源：
  - 設計圖（Figma/Sketch/圖片）
  - API 文檔或規格
  - 資源檔案（圖片、字串、顏色等）
  - 第三方套件或 SDK
- **主動提問**確認不清楚的需求：
  - UI/UX 細節
  - 業務邏輯細節
  - 邊界條件處理
  - 錯誤處理策略
- **列出缺少的資源**並請你補充

### 2.5 🔍 Root Cause 分析（Bug 類型必做）

**重要：對於 Bug 類型的 issue，必須在建立 TODO 清單和開始修復之前，先完成 root cause 分析並取得使用者確認。**

執行步驟：
1. **深入研讀程式碼**：根據 bug 描述和重現步驟，搜尋並閱讀所有相關的程式碼檔案
2. **追蹤執行路徑**：從觸發點（如使用者操作、API 回應）開始，逐步追蹤程式碼的執行路徑
3. **定位根本原因**：找出導致 bug 的真正原因（而非表面症狀）
4. **向使用者報告分析結果**：
   - 清楚說明 root cause 是什麼
   - 列出涉及的檔案和程式碼位置
   - 說明為什麼會發生這個問題
   - 提出修復方案（可能有多個方案時列出各方案的優缺點）
5. **等待使用者確認**：在使用者確認分析正確且同意修復方案後，才進入下一步

報告格式範例：
```
🔍 Root Cause 分析結果

📋 問題描述：
使用者刪除帳號後重新登入，無法顯示設定暱稱頁面

🎯 根本原因：
Firebase Auth 在本地保留了 session 快取。刪除帳號時雖然清除了
後端資料和 UserSessionManager，但沒有清除 Firebase Auth 的
session。下次第三方登入時，Firebase 使用舊的快取 token，
導致後端無法識別為新帳號。

📁 涉及檔案：
- LoginViewModel.kt:661-691 (登入判斷邏輯)
- LoginViewModel.kt:728-732 (logout 函數)
- UserSessionManager.kt:54-75 (cleanSession 函數)

🔧 建議修復方案：
在 logout() 和 accountDelete() 中呼叫 Firebase.auth.signOut()
清除 Firebase Auth session。

❓ 請確認：
1. 以上分析是否正確？
2. 是否同意此修復方案？
```

**注意**：
- 不得跳過 root cause 分析直接開始修復
- 分析必須找到「根本原因」，而非僅描述「表面現象」
- 如果無法確定 root cause，應誠實告知並列出可能的原因，與使用者討論

### 3. ✅ 創建 TODO 清單
使用 TaskCreate 創建結構化的待辦事項，例如：
- [ ] 分析現有程式碼結構
- [ ] 創建/修改 ViewModel
- [ ] 實作 UI 組件
- [ ] 添加網路 API 呼叫
- [ ] 處理錯誤情況
- [ ] 添加單元測試（如需要）
- [ ] 更新相關文檔

每個任務都會包含：
- **subject**: 清晰的任務標題
- **description**: 詳細的實作內容
- **activeForm**: 執行中的狀態顯示

### 4. 🔧 依序執行任務
- 按照 TODO 清單逐一完成任務
- 使用 TaskUpdate 更新任務狀態：
  - `pending` → `in_progress` → `completed`
- 每完成一個任務會自動進入下一個
- 如遇到問題會暫停並詢問你的意見

### 5. ✨ 完成與驗證
- 所有任務完成後進行最終檢查
- 確認符合 Jira issue 的驗收條件
- 提供測試建議和驗證步驟

## 智能提問功能

我會在以下情況主動詢問：

### 缺少必要資源時
- **設計圖缺失**: 「我需要 XX 頁面的設計圖，請提供 Figma 連結或截圖」
- **API 規格不明**: 「請提供 XX API 的 request/response 格式」
- **字串資源未定義**: 「請提供按鈕文字和錯誤訊息的內容」
- **圖片素材缺少**: 「需要 XX icon，請提供 SVG 或 PNG 檔案」

### 需求不清楚時
- **UI 互動細節**: 「點擊 XX 按鈕後應該跳轉到哪個頁面？」
- **資料來源**: 「XX 資料應該從本地快取還是即時從 API 獲取？」
- **邊界條件**: 「如果用戶未登入，應該顯示什麼？」
- **錯誤處理**: 「網路錯誤時應該顯示 Toast 還是 Dialog？」

### 技術選擇時
- **架構決策**: 「這個功能應該用 MVI 還是 MVVM？」
- **套件選擇**: 「日期選擇要用系統原生還是第三方套件？」
- **效能考量**: 「這個列表預計會有多少筆資料？需要分頁嗎？」

## 前置條件

執行此 skill 前請確保：

- ✅ 已配置 Jira MCP server (`jira-extended`) 用於讀取 issue 資訊
- ✅ 當前在 git repository 中
- ✅ 開發環境已設置完成
- ✅ 可以執行 Android Studio 編譯
- ✅ 有足夠的資訊來理解 issue 需求（或準備好回答我的問題）

## 完整示例

假設你要實作 EK-920: 「新增深色模式切換功能」

執行：
```bash
/jira-task EK-920
```

**自動執行流程：**

**步驟 1 - 分析 Issue**
```
✅ 已獲取 Jira issue: "新增深色模式切換功能"
📋 類型: Story
🎯 優先級: High

需求摘要：
- 在設定頁面新增深色模式開關
- 支援系統自動、淺色、深色三種模式
- 切換時即時生效，不需重啟 App
```

**步驟 2 - 需求確認（我會詢問）**
```
我需要確認以下事項：

❓ 設計相關：
1. 深色模式的配色方案是什麼？請提供設計稿或色票
2. 開關 UI 應該用 Switch 還是 RadioButton？

❓ 技術細節：
3. 深色模式設定應該存在哪裡（SharedPreferences/DataStore）？
4. 是否需要平滑的過渡動畫？

📦 需要的資源：
- [ ] 設定頁面的設計圖（包含深色模式開關位置）
- [ ] 深色模式的 color palette（主色、背景色、文字色等）
- [ ] 月亮/太陽 icon（如需要）
```

**步驟 3 - 創建 TODO 清單**
```
✅ 已創建 8 個任務：

1. [ ] 分析現有主題系統實作
2. [ ] 定義深色模式 colors.xml 和 themes.xml
3. [ ] 實作 ThemeManager 管理主題切換
4. [ ] 在 SettingsViewModel 添加主題設定邏輯
5. [ ] 在 SettingsScreen 添加主題切換 UI
6. [ ] 實作主題即時切換功能
7. [ ] 處理系統主題變更監聽
8. [ ] 測試所有頁面在深色模式下的顯示
```

**步驟 4 - 開始執行**
```
▶️  正在執行任務 1/8: 分析現有主題系統實作

[讀取相關文件...]
[分析 Theme.kt、colors.xml 等...]

✅ 任務 1 完成

▶️  正在執行任務 2/8: 定義深色模式 colors.xml 和 themes.xml

[創建 colors-night.xml...]
[更新 themes.xml...]

✅ 任務 2 完成

... (繼續執行所有任務)
```

**步驟 5 - 完成**
```
🎉 所有任務已完成！

✅ 完成摘要：
- 已實作深色模式切換功能
- 支援系統自動、淺色、深色三種模式
- 切換即時生效，無需重啟
- 所有頁面都已適配深色模式

🧪 建議測試步驟：
1. 進入設定頁面，切換不同主題模式
2. 確認所有頁面顏色正確顯示
3. 測試系統主題變更時 App 的反應
4. 確認主題設定在 App 重啟後保留

📝 下一步：
- 可以執行 /jira-pr EK-920 創建 Pull Request
- 或手動測試功能是否符合需求
```

## 參數說明

| 參數 | 類型 | 必填 | 說明 | 示例 |
|-----|------|------|------|------|
| Jira URL/Key | String | 可選 | Jira issue 的 URL 或 Key | `EK-920` 或 `https://showyouapp.atlassian.net/browse/EK-920` |

如果不提供參數，我會詢問你要處理哪個 Jira issue。

## 互動式執行

此 skill 是**互動式**的，我會在執行過程中：

### 📊 即時進度顯示
- 顯示當前執行的任務
- 更新任務完成狀態
- 預估剩餘任務數量

### 💬 主動溝通
- 需要決策時詢問你的選擇
- 發現問題時立即報告
- 需要額外資源時明確說明

### 🔄 靈活調整
- 根據你的回饋調整實作方向
- 如果某個方案不可行，會提出替代方案
- 可以隨時暫停、跳過或重新執行任務

## 支援的 Issue 類型

| Jira Issue Type | 處理方式 | 示例 |
|----------------|---------|------|
| 🐛 Bug | 分析問題 → **Root Cause 分析 → 使用者確認** → 修復 → 測試 | 修復登入頁崩潰問題 |
| ✨ Story/Feature | 需求分析 → 設計方案 → 實作 → 驗證 | 新增社群分享功能 |
| 🔧 Task | 理解目標 → 規劃步驟 → 執行 → 確認 | 重構網路層架構 |
| 📈 Improvement | 評估現況 → 提出改進 → 實作 → 測試 | 優化列表載入效能 |

## 與其他 Skills 的配合

此 skill 可以與其他 skills 搭配使用：

### 搭配 `/jira-pr`
```bash
# 1. 先用 jira-task 完成實作
/jira-task EK-920

# 2. 完成後用 jira-pr 創建 PR
/jira-pr EK-920
```

### 搭配 `/compose`
```bash
# 1. 用 jira-task 分析需求和創建 TODO
/jira-task EK-921

# 2. 當需要創建 Compose 組件時，可以使用 compose skill
/compose ProfileScreen

# 3. 繼續完成剩餘任務
```

## 進階用法

### 部分執行
如果你只想分析需求而不實作：
```bash
# 執行後在創建 TODO 清單時告訴我「先不要開始實作」
/jira-task EK-920
```

### 繼續未完成的任務
如果之前執行中斷了：
```bash
# 我會檢查現有的 TODO 清單並繼續執行
/jira-task EK-920
```

### 僅分析特定部分
```bash
# 在對話中明確指示
/jira-task EK-920
「只分析 UI 部分，ViewModel 我自己處理」
```

## 故障排除

### Q: 無法存取 Jira Issue

**解決方案：**
1. **檢查 MCP 連接**：
   ```bash
   # 使用 /mcp 命令檢查 Jira MCP server 狀態
   /mcp
   ```

2. **驗證 MCP server**：
   - 確認 `jira-extended` MCP server 已正確配置
   - 測試是否能讀取其他 issue

3. **檢查 Issue Key**：
   - 確認 issue key 格式正確（例如：EK-920）
   - 確認 issue 存在且你有權限查看

### Q: 不確定某個需求怎麼做

**不用擔心！** 這正是此 skill 的設計目的：
- 我會主動詢問不清楚的部分
- 你只需要回答我的問題即可
- 如果你也不確定，我們可以一起討論可能的方案

### Q: 實作過程中遇到問題

**我會：**
- 立即暫停並報告問題
- 提出可能的解決方案
- 等待你的決策後繼續

### Q: 需要調整某個已完成的任務

**沒問題！**
```bash
# 告訴我需要修改什麼
「請修改 ViewModel 的部分，XXX 邏輯需要調整」
```

## 最佳實踐

### ✅ 執行前準備
1. 確保 Jira issue 描述清晰
2. 準備好相關的設計圖和資源
3. 了解基本的需求背景

### ✅ 執行中配合
1. 及時回答我的提問
2. 提供清晰的資源連結或檔案
3. 如有疑問隨時打斷討論

### ✅ 執行後檢查
1. 執行單元測試（如有）
2. 手動測試主要流程
3. 確認符合驗收條件

## 配置

預設行為（可在執行時調整）：

- **分析深度**: 完整分析（可要求簡化）
- **TODO 粒度**: 中等（可要求更細或更粗）
- **提問頻率**: 主動（可要求減少提問）
- **程式碼風格**: 遵循專案現有規範

## 技術實現

此 skill 使用以下工具：

1. **Jira MCP Server (`jira-extended`)** - 獲取 issue 資訊
   - 讀取 issue 的 summary、description、type 等
   - 只進行讀取操作，不修改 Jira issue
2. **TaskCreate/TaskUpdate/TaskList** - 管理 TODO 清單
3. **AskUserQuestion** - 互動式提問
4. **Read/Write/Edit** - 程式碼操作
5. **Glob/Grep** - 程式碼搜尋和分析

所有操作都會保持透明，你可以隨時了解我在做什麼。

---

## 🎯 開始使用

準備好了嗎？只需要執行：

```bash
/jira-task <你的 Issue Key 或 URL>
```

我會引導你完成整個實作流程！
