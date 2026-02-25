# Jira Task Skill - 完整文檔

自動化 Jira issue 分析、實作、驗證的完整解決方案。

## 📖 目錄

- [概述](#概述)
- [核心功能](#核心功能)
- [工作原理](#工作原理)
- [使用指南](#使用指南)
- [互動模式](#互動模式)
- [最佳實踐](#最佳實踐)
- [進階技巧](#進階技巧)
- [故障排除](#故障排除)
- [範例集](#範例集)

## 概述

`/jira-task` 是一個智能的 Jira 任務執行 skill，能夠：

1. **自動分析** Jira issue 的需求和驗收條件
2. **主動提問** 確認不清楚的細節和缺少的資源
3. **創建 TODO** 結構化的任務清單
4. **依序執行** 逐步完成所有實作
5. **驗證結果** 確保符合需求

### 與其他工具的區別

| 功能 | /jira-task | /jira-pr | 手動開發 |
|------|-----------|----------|---------|
| 分析需求 | ✅ 自動 | ❌ | 👤 手動 |
| 提問確認 | ✅ 主動 | ❌ | 👤 手動 |
| 任務規劃 | ✅ 自動 | ❌ | 👤 手動 |
| 程式碼實作 | ✅ 自動 | ❌ | 👤 手動 |
| 創建 PR | ❌ | ✅ 自動 | 👤 手動 |

**推薦工作流程:**
```
/jira-task (分析+實作) → /jira-pr (創建PR) → /qa-release (發布QA)
```

## 核心功能

### 🔍 智能需求分析

- 解析 Jira issue 的所有欄位
- 提取關鍵需求和驗收條件
- 分析相關的 comments 和附件
- 識別技術挑戰和風險點

### 🔄 Git 工作流程管理

每個 Jira issue 完成後自動處理 git 操作：

#### 執行前準備
- ✅ **檢查 git 狀態**：確保工作區乾淨
- ✅ **自動 stash**：如有未提交變更，自動 stash 保存
- ✅ **記錄 stash 資訊**：方便任務完成後恢復

#### 執行後提交
- ✅ **創建 feature branch**：從 dev branch 創建獨立分支
- ✅ **規範命名**：使用 `feat/{ISSUE-KEY}-{short-summary}` 格式
- ✅ **智能提交**：只 stage 相關的變更檔案
- ✅ **規範訊息**：使用統一的 commit message 格式

#### Branch 命名範例
```bash
feat/EK-995-fix-newcomer-bonus-timing
feat/EK-978-fix-guest-task-navigation
feat/EK-920-add-dark-mode-toggle
```

#### Commit 訊息範例
```
[EK-995] 修正新人獎勵時間驗證邏輯

- 在點擊登入按鈕時記錄活動期間狀態
- 修改 LoginViewModel 保存按鈕點擊時的活動狀態
- 在登入 API 呼叫時使用保存的活動狀態

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

### 💬 主動互動式提問

我會在以下情況主動詢問：

#### 1. 缺少設計資源
```
📐 需要 XX 頁面的設計圖

請提供以下任一格式：
- Figma/Sketch 連結
- 截圖或原型圖
- 或描述 UI 應該如何呈現
```

#### 2. API 規格不明確
```
📡 需要 XX API 的規格

請提供：
- API endpoint URL
- Request body 格式
- Response 格式
- 認證方式（如需要）
```

#### 3. UI/UX 細節不清楚
```
🎨 需要確認 UI 互動細節

1. 使用者點擊「儲存」後應該？
   a) 留在當前頁面並顯示 Toast
   b) 返回上一頁
   c) 跳轉到其他頁面

2. 載入中要顯示什麼？
   a) Loading spinner
   b) Skeleton screen
   c) 按鈕 disabled
```

#### 4. 業務邏輯決策
```
🔧 需要確認業務邏輯

當使用者未登入時，點擊「收藏」應該？
a) 直接跳轉到登入頁
b) 顯示登入 Dialog
c) 顯示提示並留在當前頁
```

#### 5. 技術選擇
```
⚙️ 需要技術決策

這個功能的資料儲存方式？
a) 使用 SharedPreferences（簡單鍵值對）
b) 使用 Room Database（複雜資料結構）
c) 只存在記憶體（不需持久化）
```

### ✅ TODO 清單管理

自動創建結構化的任務清單，例如：

```
實作「使用者個人資料編輯」功能

任務清單（共 8 項）：

1. [ ] 分析現有 Profile 相關程式碼
    - 搜尋現有的 ProfileScreen、ProfileViewModel
    - 了解現有的資料結構和 API

2. [ ] 創建 ProfileEditScreen Compose UI
    - 使用 /compose skill 創建基本結構
    - 實作表單欄位（暱稱、簡介）
    - 添加頭像上傳區域

3. [ ] 實作 ProfileEditViewModel
    - 定義 State（編輯中的資料）
    - 定義 Event（使用者操作）
    - 實作表單驗證邏輯

4. [ ] 整合頭像上傳 API
    - 實作圖片選擇功能
    - 壓縮和上傳圖片
    - 處理上傳進度顯示

5. [ ] 實作儲存功能
    - 呼叫更新 API
    - 處理成功/失敗情況
    - 更新本地快取

6. [ ] 添加表單驗證
    - 暱稱長度驗證（2-20字）
    - 簡介長度驗證（最多200字）
    - 即時顯示錯誤提示

7. [ ] 處理邊界情況
    - 網路錯誤處理
    - API 回傳錯誤處理
    - 離開時未儲存提醒

8. [ ] 測試完整流程
    - 正常編輯和儲存
    - 各種錯誤情況
    - 不同螢幕尺寸適配
```

### 🔄 依序執行任務

每個任務的執行流程：

1. **標記為執行中** (`in_progress`)
2. **執行實作**
   - 搜尋相關檔案
   - 讀取現有程式碼
   - 寫入或修改檔案
   - 確保符合專案規範
3. **自我檢查**
   - 檢查語法錯誤
   - 確認邏輯正確
   - 驗證符合需求
4. **標記為完成** (`completed`)
5. **進入下一個任務**

如果遇到問題：
- 🚨 暫停執行
- 💬 報告問題
- 🤔 提出解決方案
- ⏳ 等待你的決策

## 工作原理

### 執行流程圖

```
開始
  ↓
獲取 Jira Issue 資訊
  ↓
分析需求和驗收條件 ←─────┐
  ↓                      │
識別缺少的資源和不清楚的細節  │
  ↓                      │
提問並等待回答              │
  ↓                      │
資訊完整了嗎？ ─ NO ──────┘
  ↓ YES
是 Bug 類型？ ─ YES ─→ Root Cause 分析
  ↓ NO                  ↓
  │              向使用者報告分析結果
  │                     ↓
  │              使用者確認？ ─ NO ─→ 重新分析
  │                     ↓ YES
  └────────────────────┘
  ↓
創建 TODO 清單
  ↓
顯示清單並確認
  ↓
┌─────────────────────┐
│  Git 執行前檢查      │
└─────────────────────┘
  ↓
檢查 git 工作區狀態
  ↓
有未提交變更？ ─ YES ─→ 自動 stash
  ↓ NO                  ↓
  └────────────────────┘
  ↓
開始執行第一個任務 ←─────┐
  ↓                    │
執行任務實作              │
  ↓                    │
遇到問題？ ─ YES ─→ 提問並等待
  ↓ NO                 │
標記任務完成 ←───────────┘
  ↓
還有未完成的任務？ ─ YES ─┘
  ↓ NO
最終驗證
  ↓
┌─────────────────────┐
│  Git 提交流程        │
└─────────────────────┘
  ↓
從 dev 創建 feature branch
  ↓
Stage 變更的檔案
  ↓
Commit 變更
  ↓
顯示 branch 和 commit 資訊
  ↓
提示 stashed 變更（如有）
  ↓
完成報告
  ↓
結束
```

### 技術架構

```
┌─────────────────────────────────────┐
│         Jira Task Skill             │
├─────────────────────────────────────┤
│                                     │
│  ┌──────────────────────────────┐  │
│  │   需求分析引擎                │  │
│  │  - Jira API 整合             │  │
│  │  - 需求提取                  │  │
│  │  - 缺口識別                  │  │
│  └──────────────────────────────┘  │
│              ↓                      │
│  ┌──────────────────────────────┐  │
│  │   互動問答引擎                │  │
│  │  - AskUserQuestion          │  │
│  │  - 資源請求                  │  │
│  │  - 決策確認                  │  │
│  └──────────────────────────────┘  │
│              ↓                      │
│  ┌──────────────────────────────┐  │
│  │   任務規劃引擎                │  │
│  │  - TaskCreate               │  │
│  │  - 依賴分析                  │  │
│  │  - 優先級排序                │  │
│  └──────────────────────────────┘  │
│              ↓                      │
│  ┌──────────────────────────────┐  │
│  │   程式碼執行引擎              │  │
│  │  - Glob/Grep (搜尋)          │  │
│  │  - Read (讀取)               │  │
│  │  - Write/Edit (修改)         │  │
│  │  - TaskUpdate (進度)         │  │
│  └──────────────────────────────┘  │
│              ↓                      │
│  ┌──────────────────────────────┐  │
│  │   驗證測試引擎                │  │
│  │  - 語法檢查                  │  │
│  │  - 邏輯驗證                  │  │
│  │  - 需求對照                  │  │
│  └──────────────────────────────┘  │
│                                     │
└─────────────────────────────────────┘
```

## 使用指南

### 基本使用

```bash
# 使用 Issue Key
/jira-task EK-920

# 使用完整 URL
/jira-task https://showyouapp.atlassian.net/browse/EK-920

# 不提供參數（會提示輸入）
/jira-task
```

### 參數說明

| 參數 | 類型 | 必填 | 說明 |
|-----|------|------|------|
| issue_identifier | String | 可選 | Jira issue 的 Key 或完整 URL |

### Git 工作流程說明

#### 執行前的 Git 檢查

當你執行 `/jira-task` 時，我會首先檢查 git 狀態：

```bash
# 檢查工作區狀態
git status --porcelain

# 如果有未提交的變更
→ 自動執行 stash
→ 記錄 stash 訊息
→ 繼續執行任務
```

**Stash 訊息格式：**
```
Auto stash before jira-task EK-995 at 2026-02-04_21-30-00
```

#### 執行後的 Git 提交

所有任務完成後，我會自動：

1. **切換到 dev branch**
   ```bash
   git checkout dev
   git pull origin dev
   ```

2. **創建 feature branch**
   ```bash
   # 格式: feat/{ISSUE-KEY}-{short-summary}
   git checkout -b feat/EK-995-fix-newcomer-bonus-timing
   ```

3. **Stage 變更的檔案**
   ```bash
   # 只 add 實際修改的檔案
   git add app/src/.../LoginViewModel.kt
   git add app/src/.../LoginPage.kt
   ```

4. **提交變更**
   ```bash
   git commit -m "[EK-995] 修正新人獎勵時間驗證邏輯

   - 在點擊登入按鈕時記錄活動期間狀態
   - 修改 LoginViewModel 保存按鈕點擊時的活動狀態
   - 在登入 API 呼叫時使用保存的活動狀態

   Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
   ```

5. **顯示結果**
   ```
   ✅ Branch 已創建: feat/EK-995-fix-newcomer-bonus-timing
   ✅ 變更已提交: abc123d

   📝 Stashed 變更:
   stash@{0}: Auto stash before jira-task EK-995...

   下一步:
   - 檢查程式碼變更: git diff dev
   - 推送到 remote: git push origin feat/EK-995-fix-newcomer-bonus-timing
   - 創建 PR: /jira-pr EK-995
   - 恢復 stash: git stash pop (如需要)
   ```

#### 自定義 Git 行為

```bash
# 禁用自動 stash（遇到未提交變更時中止）
/jira-task EK-995 --no-stash

# 指定不同的基礎 branch（預設為 dev）
/jira-task EK-995 --base-branch=main

# 完成後不自動 commit（僅執行任務）
/jira-task EK-995 --no-commit

# 完成後自動推送到 remote
/jira-task EK-995 --auto-push
```

### 回應我的提問

#### 格式 1: 直接回答
```
你：/jira-task EK-920

我：需要 XX 頁面的設計圖，請提供 Figma 連結

你：https://figma.com/file/abc123
```

#### 格式 2: 結構化回答
```
我：需要確認以下問題：
   1. XXX?
   2. YYY?
   3. ZZZ?

你：
   1. 答案 A
   2. 答案 B
   3. 答案 C
```

#### 格式 3: 提供檔案
```
我：需要登入頁面的設計圖

你：[拖曳圖片到對話框]
   這是設計圖，主要注意...
```

## 互動模式

### 提問類型

#### 1. 是非題
```
❓ 儲存成功後要關閉頁面嗎？

回答：是 / 否
```

#### 2. 選擇題
```
❓ 深色模式開關使用哪種 UI？

a) Switch 切換開關
b) RadioButton 單選按鈕
c) Dropdown 下拉選單

回答：a / b / c
```

#### 3. 開放式問題
```
❓ 搜尋結果為空時應該顯示什麼訊息？

回答：[你的答案]
```

#### 4. 資源請求
```
📦 需要以下資源：

- [ ] 錯誤頁面的插圖（SVG 或 PNG）
- [ ] 空狀態的文案內容
- [ ] 預設頭像圖片

請提供上述資源的檔案或連結
```

### 控制指令

執行過程中你可以隨時說：

| 指令 | 效果 |
|-----|------|
| 「暫停」 | 暫停當前任務執行 |
| 「繼續」 | 繼續執行任務 |
| 「跳過這個任務」 | 跳過當前任務 |
| 「重新執行這個任務」 | 重新執行當前任務 |
| 「停止」 | 完全停止 skill 執行 |
| 「顯示進度」 | 顯示當前 TODO 清單狀態 |

## 最佳實踐

### ✅ 準備工作

#### Git 環境準備

執行 `/jira-task` 前的 git 檢查：

```bash
# 1. 確認當前 branch
git branch
→ 建議在 dev branch 或 feature branch

# 2. 確認 dev branch 是最新的
git checkout dev
git pull origin dev

# 3. 檢查是否有未提交的變更
git status
→ 有變更？沒關係，/jira-task 會自動 stash

# 4. 確認 remote 連接正常
git remote -v
```

**不用擔心的情況：**
- ✅ 有未提交的變更 → 自動 stash
- ✅ 不在 dev branch → 會自動切換
- ✅ dev branch 過舊 → 會自動 pull

**需要注意的情況：**
- ⚠️ git 衝突未解決 → 請先手動解決
- ⚠️ 沒有 dev branch → 請先創建或指定其他基礎 branch

#### Jira Issue 撰寫
```markdown
標題：
新增社群分享功能

描述：
## 需求
使用者可以分享貼文到 Facebook 和 Twitter

## 功能細節
1. 在貼文詳情頁添加「分享」按鈕
2. 點擊後顯示分享選項（FB、Twitter）
3. 選擇平台後顯示分享預覽
4. 確認後執行分享並顯示成功提示

## 驗收條件
- [ ] 可以成功分享到 Facebook
- [ ] 可以成功分享到 Twitter
- [ ] 分享預覽顯示正確
- [ ] 分享失敗有錯誤處理

## 設計資源
- 設計圖: https://figma.com/...
- Icon 素材: [附件]

## API 文檔
- Facebook SDK: [連結]
- Twitter API: [連結]
```

### ✅ 回答技巧

**好的回答：**
```
✅ 清晰具體
「按鈕文字是『立即分享』，顏色使用主題色 #FF6B6B」

✅ 提供連結
「設計圖在這：https://figma.com/file/...」

✅ 補充說明
「暱稱最多 20 字，超過要顯示錯誤訊息『暱稱過長』」
```

**避免的回答：**
```
❌ 太模糊
「隨便」「都可以」「你決定」

❌ 不完整
「設計圖在 Figma」（沒有連結）

❌ 自相矛盾
「要顯示 Loading，但不要有任何 UI 變化」
```

### ✅ 資源準備

#### 設計資源檢查清單
- [ ] UI 設計圖（Figma/Sketch/圖片）
- [ ] Icon 和圖示（SVG 或 PNG）
- [ ] 配色規範（色碼）
- [ ] 字型和文字大小
- [ ] 間距和邊距規範

#### 技術資源檢查清單
- [ ] API 文檔（endpoint、參數、回應格式）
- [ ] 第三方 SDK 文檔（如需要）
- [ ] 資料庫 schema（如需要）
- [ ] 測試帳號或測試資料

#### 內容資源檢查清單
- [ ] 按鈕文字
- [ ] 錯誤訊息文案
- [ ] 提示訊息
- [ ] 空狀態提示
- [ ] 成功訊息

## 進階技巧

### 技巧 1: 分階段執行

```bash
# 第一階段：只分析和規劃
/jira-task EK-920
> 「先幫我分析需求和列出 TODO，不要開始實作」

# 檢視 TODO 清單
> 「顯示 TODO 清單」

# 第二階段：開始實作
> 「好，現在開始實作」
```

### 技巧 2: 部分實作

```bash
/jira-task EK-920
> 「只實作 UI 部分，API 整合我自己處理」

# 我會跳過 API 相關任務
```

### 技巧 3: 搭配其他 Skills

```bash
# 1. 分析需求
/jira-task EK-920

# 2. 當需要創建複雜的 Compose 組件
/compose ProfileEditScreen

# 3. 返回繼續執行
> 「繼續執行剩餘任務」

# 4. 完成後創建 PR
/jira-pr EK-920
```

### 技巧 4: 處理大型任務

```bash
# 將大型 issue 拆分成多個子任務
# 然後分別執行

/jira-task EK-920  # 主要功能
/jira-task EK-921  # 測試
/jira-task EK-922  # 文檔
```

## 故障排除

### 問題 1: Jira 連接失敗

**症狀：**
```
❌ 無法連接到 Jira API
```

**解決方案：**
```bash
# 1. 檢查 Jira MCP server 設定
cat .claude/settings.local.json

# 2. 確認有以下設定
{
  "mcpServers": {
    "jira": {
      "env": {
        "JIRA_EMAIL": "your-email@example.com",
        "JIRA_API_TOKEN": "your-api-token"
      }
    }
  }
}

# 3. 重新啟動 Claude Code
```

### 問題 2: TODO 清單過於龐大

**症狀：**
```
創建了 20+ 個任務，感覺太多了
```

**解決方案：**
```bash
# 告訴我簡化
> 「這些任務太細了，請合併成較大的任務」

# 我會重新組織成 5-10 個更大的任務
```

### 問題 3: 實作方向不符期待

**症狀：**
```
我發現實作的架構不是我想要的
```

**解決方案：**
```bash
# 立即反應
> 「停止，這個架構不對，我希望用 XXX 方式」

# 我會：
# 1. 停止當前任務
# 2. 討論新的方案
# 3. 調整實作方向
# 4. 重新執行
```

### 問題 4: 缺少某個檔案或資源

**症狀：**
```
⚠️  找不到 XX 檔案
```

**解決方案：**
```bash
# 方案 A: 提供檔案路徑
> 「檔案在 app/src/main/java/com/example/...」

# 方案 B: 建議替代方案
> 「這個檔案不存在，我們應該創建它」

# 方案 C: 調整實作
> 「不需要這個檔案，改用 XXX 方式」
```

### 問題 5: 不知道如何回答問題

**症狀：**
```
我被問到一個技術問題，但我不知道答案
```

**解決方案：**
```bash
# 誠實表達
> 「我不確定，你有什麼建議嗎？」

# 我會：
# 1. 提供幾個常見的選項
# 2. 說明每個選項的優缺點
# 3. 給出建議
# 4. 等待你的決定
```

## 範例集

### 範例 1: 簡單 Bug 修復

**Jira Issue: EK-925**
```
標題：修復登入按鈕無法點擊的問題

描述：
在登入頁面，輸入完帳號密碼後，登入按鈕仍然是 disabled 狀態

重現步驟：
1. 打開 App
2. 輸入帳號
3. 輸入密碼
4. 發現登入按鈕無法點擊
```

**執行過程：**
```
$ /jira-task EK-925

🔍 檢查 git 狀態...
⚠️  發現未提交的變更:
   M  app/src/.../MainActivity.kt
   M  README.md

💾 自動 stash 變更...
✅ Stashed: Auto stash before jira-task EK-925 at 2026-02-04_14-30-00

✅ 已獲取 issue 資訊

📋 偵測到 Bug 類型 issue，開始 Root Cause 分析...

🔍 Root Cause 分析結果

📋 問題描述：
輸入完帳號密碼後，登入按鈕仍然是 disabled 狀態

🎯 根本原因：
LoginViewModel.kt 中的 isValid 計算邏輯有誤。
目前的判斷條件是：email.isNotEmpty() && password.isNotEmpty()
但按鈕的 enabled 狀態綁定到了 isValidForm，而 isValidForm
還額外檢查了 isValidEmail(email) 和 password.length >= 6。
兩個驗證邏輯不一致，導致即使輸入了帳號密碼，按鈕仍然不可點擊。

📁 涉及檔案：
- LoginScreen.kt:45 (按鈕的 enabled 綁定)
- LoginViewModel.kt:23 (isValid 計算邏輯)
- LoginViewModel.kt:30 (isValidForm 計算邏輯)

🔧 建議修復方案：
統一使用 isValidForm 作為按鈕的 enabled 狀態判斷，
並修正 isValid 的邏輯為：isValidEmail(email) && password.length >= 6

❓ 請確認：
1. 以上分析是否正確？
2. 是否同意此修復方案？

> 使用者回覆：分析正確，請進行修復

✅ 使用者已確認，開始建立修復任務...

✅ 已創建 2 個任務：
1. [ ] 修復 LoginViewModel 中的驗證邏輯
2. [ ] 驗證修復後的按鈕狀態

▶️  開始執行...

[1/2] 正在修復驗證邏輯...
✅ 已修復

[2/2] 正在驗證...
✅ 按鈕狀態邏輯正確

🎉 Bug 已修復！

修改文件：
- app/src/.../LoginViewModel.kt

🌿 創建 feature branch...
✅ Branch: feat/EK-925-fix-login-button-state

💾 提交變更...
✅ Commit: a1b2c3d [EK-925] 修復登入按鈕狀態邏輯

📝 Stashed 變更:
stash@{0}: Auto stash before jira-task EK-925...

下一步:
- 檢查變更: git diff dev
- 推送 branch: git push origin feat/EK-925-fix-login-button-state
- 創建 PR: /jira-pr EK-925
- 恢復 stash: git stash pop (如需要)

建議測試：
1. 輸入有效的 email 和密碼（6 位以上）→ 按鈕應可點擊
2. 輸入無效的 email → 按鈕應不可點擊
3. 輸入密碼少於 6 位 → 按鈕應不可點擊
```

### 範例 2: 新功能實作

**Jira Issue: EK-930**
```
標題：新增貼文收藏功能

描述：
使用者可以收藏喜歡的貼文

功能需求：
1. 貼文列表和詳情頁都要有收藏按鈕
2. 點擊後切換收藏狀態
3. 收藏的貼文可以在「我的收藏」頁面查看

API:
POST /api/posts/{id}/favorite
DELETE /api/posts/{id}/favorite
GET /api/users/me/favorites

設計圖：
https://figma.com/file/...
```

**執行過程：**
```
$ /jira-task EK-930

✅ 已獲取 issue 資訊

❓ 需要確認：
1. 收藏按鈕的 icon 是實心還是空心愛心？
2. 收藏成功要顯示 Toast 提示嗎？
3. 收藏列表需要分頁嗎？

📦 需要資源：
- [ ] 愛心 icon（已收藏、未收藏兩個狀態）

> 回答：
> 1. 空心 → 實心
> 2. 要，顯示「已加入收藏」
> 3. 需要，每頁 20 筆

> 這是 icon：[圖片]

✅ 收到資訊，開始規劃...

✅ 已創建 10 個任務：
1. [ ] 定義收藏相關的 data models
2. [ ] 實作收藏 API service
3. [ ] 創建 FavoriteRepository
4. [ ] 在 PostItem 添加收藏按鈕 UI
5. [ ] 實作收藏切換邏輯
6. [ ] 創建「我的收藏」頁面 UI
7. [ ] 實作收藏列表載入（含分頁）
8. [ ] 添加收藏狀態的本地快取
9. [ ] 處理收藏失敗的錯誤情況
10. [ ] 測試完整流程

▶️  開始執行...

[1/10] 正在定義 data models...
✅ 已創建 FavoriteRequest.kt, FavoriteResponse.kt

[2/10] 正在實作 API service...
✅ 已添加 favoritePost(), unfavoritePost(), getFavorites()

... (繼續執行)

🎉 收藏功能已完成！

新增文件：
- data/model/FavoriteRequest.kt
- data/model/FavoriteResponse.kt
- data/repository/FavoriteRepository.kt
- ui/favorite/FavoriteScreen.kt
- ui/favorite/FavoriteViewModel.kt

修改文件：
- ui/post/PostItem.kt (添加收藏按鈕)
- ui/post/PostDetailScreen.kt (添加收藏按鈕)
- di/RepositoryModule.kt (注入 FavoriteRepository)

🌿 創建 feature branch...
✅ Branch: feat/EK-930-add-post-favorite-feature

💾 提交變更...
✅ Commit: d4e5f6g [EK-930] 新增貼文收藏功能

📋 Commit 內容:
[EK-930] 新增貼文收藏功能

- 實作收藏/取消收藏 API 整合
- 在貼文列表和詳情頁添加收藏按鈕
- 創建「我的收藏」頁面並支援分頁
- 添加本地快取以提升使用體驗
- 處理各種錯誤情況和邊界條件

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>

下一步：
- 推送 branch: git push origin feat/EK-930-add-post-favorite-feature
- 創建 PR: /jira-pr EK-930
- 或手動創建 PR 並關聯 Jira issue

建議測試：
1. 在貼文列表收藏/取消收藏
2. 在貼文詳情收藏/取消收藏
3. 查看「我的收藏」頁面
4. 測試收藏列表分頁載入
5. 測試網路錯誤情況
```

### 範例 3: 架構重構

**Jira Issue: EK-935**
```
標題：將網路層從 Retrofit 遷移到 Ktor

描述：
為了統一 Android 和 iOS 的網路層，需要將現有的 Retrofit
實作改為使用 Ktor Client

影響範圍：
- 所有 API service
- 網路錯誤處理
- 請求攔截器
```

**執行過程：**
```
$ /jira-task EK-935

✅ 已獲取 issue 資訊

⚠️  這是一個大型重構任務

❓ 需要確認：
1. 是否要一次性遷移所有 API？還是分批進行？
2. Ktor 版本要用哪個？
3. 是否需要保持與現有程式碼的相容性？
4. 測試策略是什麼？

> 回答：
> 1. 分批，先遷移登入相關 API
> 2. Ktor 2.3.7
> 3. 是，要能同時支援兩種實作
> 4. 每個 API 都要寫整合測試

✅ 了解，這次先處理登入相關 API

✅ 已創建 12 個任務：
1. [ ] 添加 Ktor dependencies
2. [ ] 創建 Ktor HttpClient 設定
3. [ ] 實作 Ktor 版本的認證攔截器
4. [ ] 實作 Ktor 版本的錯誤處理
5. [ ] 遷移 AuthApiService (登入、註冊)
6. [ ] 創建 API service 的抽象層
7. [ ] 實作 feature flag 切換機制
8. [ ] 添加 Ktor API 的單元測試
9. [ ] 添加整合測試
10. [ ] 更新 DI module
11. [ ] 測試登入流程
12. [ ] 撰寫遷移文檔

▶️  開始執行...

... (執行過程)

🎉 第一階段遷移完成！

✅ 已完成：
- Ktor 基礎設施建立
- 登入相關 API 已遷移
- Feature flag 機制已實作
- 測試已通過

📝 遷移文檔：docs/ktor-migration.md

下一步建議：
1. 在 QA 環境測試 1-2 天
2. 確認無問題後再遷移其他 API
3. 可創建新的 issue 來追蹤後續遷移
```

## Git 工作流程完整範例

完整的端到端工作流程：

```bash
# 初始狀態：你正在開發中，有一些未提交的變更
$ git status
M  app/src/.../MainActivity.kt
M  README.md

# 執行 jira-task
$ /jira-task EK-995

🔍 檢查 git 狀態...
⚠️  發現未提交的變更

💾 自動 stash...
Saved working directory and index state
✅ Stashed: Auto stash before jira-task EK-995 at 2026-02-04_21-00-00

🔄 切換到 dev branch...
✅ 已更新 dev branch

[... 分析、規劃、執行任務 ...]

🎉 任務完成！

🌿 創建 feature branch...
$ git checkout -b feat/EK-995-fix-newcomer-bonus-timing
✅ Branch: feat/EK-995-fix-newcomer-bonus-timing

📝 Stage 變更...
$ git add app/src/.../LoginViewModel.kt
$ git add app/src/.../LoginPage.kt

💾 Commit...
$ git commit -m "[EK-995] 修正新人獎勵時間驗證邏輯

- 在點擊登入按鈕時記錄活動期間狀態
- 修改 LoginViewModel 保存按鈕點擊時的活動狀態
- 在登入 API 呼叫時使用保存的活動狀態

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

✅ Commit: a1b2c3d

📊 完成摘要:
├─ Branch: feat/EK-995-fix-newcomer-bonus-timing
├─ Commit: a1b2c3d
└─ 修改檔案: 2 個

📝 有 stashed 變更:
stash@{0}: Auto stash before jira-task EK-995...

下一步:
1. 推送 branch: git push origin feat/EK-995-fix-newcomer-bonus-timing
2. 創建 PR: /jira-pr EK-995
3. 恢復之前的工作: git stash pop

# 推送到 remote
$ git push origin feat/EK-995-fix-newcomer-bonus-timing

# 創建 PR（使用 jira-pr skill）
$ /jira-pr EK-995

# 恢復之前 stashed 的變更（如需要）
$ git stash pop
```

## 總結

`/jira-task` 是一個強大的自動化工具，能夠：

✅ 大幅減少從需求到實作的時間
✅ 確保不遺漏關鍵細節
✅ 主動發現和解決問題
✅ 保持實作的一致性和品質
✅ 自動處理 git 工作流程
✅ 創建規範的 branch 和 commit

### 完整工作流程
```
/jira-task EK-XXX  →  分析 + 實作 + Git Commit
       ↓
/jira-pr EK-XXX    →  創建 Pull Request
       ↓
/qa-release        →  發布到 QA 環境
```

**立即開始使用：**
```bash
/jira-task <your-issue-key>
```

有任何問題或建議，歡迎隨時告訴我！
