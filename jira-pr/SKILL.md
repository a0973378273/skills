---
name: jira-pr
description: 自動創建 PR 到 dev branch。可從 Jira issue 獲取資訊，或在無 Jira issue 時智能分析代碼修改來生成 PR。包括獲取/分析資訊、創建 branch、智能分組提交、自動推送和生成 PR。當需要創建 PR 或自動化 git 工作流時使用此 skill。
---

# 智能 PR 創建

自動化從程式碼修改到 Pull Request 的完整流程。支援兩種模式：

1. **Jira 模式**：從 Jira issue 獲取資訊（有對應 issue 時使用）
2. **智能分析模式**：分析程式碼修改自動生成 PR 描述（無 Jira issue 時使用）

## 快速使用

使用 Issue Key（Jira 模式）：
```bash
/jira-pr EK-907
```

使用完整 URL（Jira 模式）：
```bash
/jira-pr https://showyouapp.atlassian.net/browse/EK-907
```

不提供參數（智能分析模式）：
```bash
/jira-pr
```

## 執行流程

當你執行這個 skill 時，我會自動完成以下步驟：

### 模式選擇
- **如果提供 Jira URL/Key**：使用 Jira 模式
- **如果沒有提供參數**：使用智能分析模式

---

### Jira 模式流程

#### 1. 獲取 Jira Issue 資訊
- 解析提供的 Jira URL 或 Issue Key（如：EK-907）
- 使用 Jira MCP server 獲取 issue 詳細資訊
- 提取 summary、description、issue type 等

#### 2. 創建 Branch
- 從 `dev` branch 創建新的 feature/bugfix branch
- Branch 命名規則：
  - **Bug/漏洞**：`fix/EK-XXX-{summary-slug}`
  - **Feature/Story/Task**：`feat/EK-XXX-{summary-slug}`
- 自動將 summary 轉換為 kebab-case
- 如果當前有未提交的修改，會自動處理

---

### 智能分析模式流程

#### 1. 分析程式碼修改
- 使用 `git status` 和 `git diff` 檢查所有未提交的修改
- 使用 `git log` 查看最近的 commit 訊息風格
- 分析修改的檔案類型、函數、類別名稱
- 理解修改的意圖和目的（例如：bug fix、新功能、重構等）

#### 2. 智能生成 PR 資訊
根據程式碼分析自動生成：
- **修改類型**：判斷是 bug fix、feature、refactor 等
- **修改摘要**：從修改內容總結出簡潔的標題
- **詳細描述**：
  - 修改了哪些檔案
  - 修改的原因和目的
  - 主要的變更內容
  - 影響範圍

#### 3. 創建 Branch
- 從 `dev` branch 創建新的 branch
- Branch 命名規則：
  - **Bug/漏洞修復**：`fix/{intelligently-generated-slug}`
  - **新功能/改進**：`feat/{intelligently-generated-slug}`
  - **重構**：`refactor/{intelligently-generated-slug}`
- 自動將摘要轉換為 kebab-case

---

### 共用流程（兩種模式都適用）

#### 智能分組提交
- 檢查當前所有未提交的修改（使用 `git diff`）
- 根據修改的文件類型自動分組：
  - AndroidManifest.xml 修改 → 單獨一個 commit
  - Activity/Fragment 修改 → 按類別分組
  - ViewModel/Repository 修改 → 按邏輯分組
  - 其他修改 → 自動歸類
- 每個 commit 訊息格式：
  - **Jira 模式**：`[EK-XXX] {清晰的描述}`
  - **智能分析模式**：`{type}: {清晰的描述}`（例如：`fix: 修正登入頁面閃退問題`）

#### Push 到 Remote
- 自動執行 `git push -u origin {branch-name}`
- 建立 upstream tracking

#### 創建 Pull Request
- 使用 `gh pr create` 創建 PR，**目標 branch 必須為 `dev`**
- **Jira 模式** PR 標題：`[EK-XXX] {Jira summary}`
- **智能分析模式** PR 標題：`{type}: {智能生成的摘要}`
- PR body 自動包含：
  - 📋 修改描述（Jira 模式從 issue 提取；智能模式從代碼分析生成）
  - 🔧 根本原因分析（如適用）
  - ✅ 解決方案說明
  - 🧪 測試場景
  - 🔗 相關連結（Jira 模式包含 issue 連結）
- 返回 PR URL

---

### Jira 模式專屬：更新 Jira Issue

**僅在 Jira 模式下執行**，創建 PR 成功後，使用 Jira MCP 工具自動更新 issue：
- **轉換狀態**：使用 `mcp__jira-extended__jira_transition_issue` 將 issue 狀態改為 "QA 測試"
  - 先使用 `mcp__jira-extended__jira_get_transitions` 獲取可用的轉換
  - 找到 "QA 測試" 對應的 transition ID 並執行轉換
- **更新受託人**：使用 `mcp__jira-extended__jira_update_issue` 將 assignee 設定為與 reporter 相同
  - 使用 `fields: {"assignee": {"accountId": "..."}}` 格式更新
- **添加評論**：使用 `mcp__jira-extended__jira_add_comment` 在 issue 底下留言
  - 首先從 **QA branch** 讀取 `gradle/libs.versions.toml` 的 `appVersionCode`（因為版本控制在 QA branch）
  - 留言格式使用 Markdown 超連結：「PR 已創建並準備合併至 dev branch: [PR #{PR_NUMBER}]({PR_URL})，修改版本為{QA_appVersionCode + 1}」
  - 例如：若 QA branch 的 appVersionCode 是 102000005，則留言：「PR 已創建並準備合併至 dev branch: [PR #110](https://github.com/SHOW-YOU-APP/ekkorn-android/pull/110)，修改版本為 102000006」

**智能分析模式**則跳過此步驟。

## 前置條件

執行此 skill 前請確保：

### 通用前置條件（兩種模式都需要）
- ✅ 當前在 git repository 中
- ✅ 有未提交的修改（staged 或 unstaged 都可以）
- ✅ 已安裝並登入 `gh` CLI（GitHub CLI）
- ✅ 當前 branch 是從 `dev` 分支出來的，或者會切換到 `dev`
- ✅ 遠端 repository 有 `dev` branch 作為 PR 目標

### Jira 模式額外需要
- ✅ 已配置 Jira MCP server (`jira-extended`)
  - 需要有權限轉換 issue 狀態
  - 需要有權限編輯 assignee 和添加評論

### 智能分析模式
- ℹ️ 不需要 Jira 連接
- ℹ️ 會自動分析 git diff、檔案修改、最近的 commit 風格來生成 PR 內容

## 完整示例

### 示例 1：Jira 模式

假設你修復了 EK-907 的問題，修改了以下文件：
- `app/src/main/AndroidManifest.xml`
- `app/src/main/java/.../MainActivity.kt`
- `app/src/main/java/.../SplashActivity.kt`

執行：
```bash
/jira-pr EK-907
```

**自動完成的操作：**

1. ✅ 獲取 Jira issue: "[Android] 當點擊進入貼文資訊頁下，縮小APP再次返回後，會莫名被退回前一頁問題"
2. ✅ 創建 branch: `fix/EK-907-fix-post-detail-activity-stack-on-resume`
3. ✅ Commit 1: `[EK-907] 修改 MainActivity launchMode 為 singleTop 以避免清除上層 Activity`
4. ✅ Commit 2: `[EK-907] 優化 SplashActivity 重啟邏輯，從 Launcher 啟動時保留 Activity Stack`
5. ✅ Push to origin: `git push -u origin fix/EK-907-fix-post-detail-activity-stack-on-resume`
6. ✅ 創建 PR 到 dev: https://github.com/SHOW-YOU-APP/ekkorn-android/pull/110
7. ✅ 更新 Jira issue:
   - 狀態改為 "QA 測試"
   - assignee 改為與 reporter 相同
   - 添加評論：「PR 已創建並準備合併至 dev branch: [PR #110](https://github.com/SHOW-YOU-APP/ekkorn-android/pull/110)，修改版本為 102000006」（從 QA branch 讀取版本號）

**完成！** 你只需要去 GitHub 查看 PR 並等待 Review。

---

### 示例 2：智能分析模式（無 Jira Issue）

假設你優化了登入流程，修改了以下文件：
- `app/src/main/java/.../LoginViewModel.kt`
- `analytics/src/main/java/.../AFTracker.kt`
- `app/src/main/java/.../NewcomerBonusBanner.kt`

執行：
```bash
/jira-pr
```

**自動完成的操作：**

1. ✅ 分析程式碼修改：
   - 檢測到 `LoginViewModel` 的邏輯變更
   - 發現 `AFTracker` 新增了追蹤事件
   - 注意到 `NewcomerBonusBanner` 的 UI 優化
2. ✅ 智能生成摘要：「優化登入流程的新手引導橫幅顯示邏輯並加強事件追蹤」
3. ✅ 判斷修改類型：Feature (feat)
4. ✅ 創建 branch: `feat/improve-login-newcomer-banner-and-tracking`
5. ✅ Commit 1: `feat: 優化 LoginViewModel 新手引導橫幅的顯示條件`
6. ✅ Commit 2: `feat: 新增 AFTracker 登入流程事件追蹤`
7. ✅ Commit 3: `feat: 改善 NewcomerBonusBanner UI 顯示效果`
8. ✅ Push to origin: `git push -u origin feat/improve-login-newcomer-banner-and-tracking`
9. ✅ 創建 PR 到 dev，包含智能生成的描述：
   ```markdown
   ## 修改描述
   優化登入流程中新手引導橫幅的顯示邏輯，並加強相關事件追蹤。

   影響範圍：
   - 登入頁面
   - 新手引導橫幅
   - 事件追蹤系統

   ## 主要變更

   ### Commit 1: 優化 LoginViewModel 新手引導橫幅的顯示條件
   - 修改文件：`app/src/main/java/.../LoginViewModel.kt`
   - 修改內容：調整新手橫幅顯示邏輯，確保僅在適當時機顯示

   ### Commit 2: 新增 AFTracker 登入流程事件追蹤
   - 修改文件：`analytics/src/main/java/.../AFTracker.kt`
   - 修改內容：新增登入相關事件的追蹤功能

   ### Commit 3: 改善 NewcomerBonusBanner UI 顯示效果
   - 修改文件：`app/src/main/java/.../NewcomerBonusBanner.kt`
   - 修改內容：優化橫幅的視覺呈現

   ## 測試場景
   - [ ] 新使用者首次登入時橫幅正常顯示
   - [ ] 現有使用者登入時橫幅不顯示
   - [ ] 事件追蹤正確記錄登入相關行為

   🤖 Generated with [Claude Code](https://claude.com/claude-code)
   ```

**完成！** 即使沒有 Jira issue，也能自動創建結構完整的 PR。

## 參數說明

| 參數 | 類型 | 必填 | 說明 | 示例 |
|-----|------|------|------|------|
| Jira URL/Key | String | 可選 | Jira issue 的 URL 或 Key。**若不提供，則啟用智能分析模式** | `EK-907` 或 `https://showyouapp.atlassian.net/browse/EK-907` |

如果不提供參數，將自動啟用**智能分析模式**，通過分析程式碼修改來生成 PR。

## Branch 命名規則

### Jira 模式

| Jira Issue Type | Branch 前綴 | 示例 |
|----------------|-----------|------|
| 漏洞 (Bug) | `fix/` | `fix/EK-907-fix-activity-stack` |
| 功能 (Story) | `feat/` | `feat/EK-908-add-dark-mode` |
| 任務 (Task) | `feat/` | `feat/EK-909-refactor-network-layer` |
| 改進 (Improvement) | `feat/` | `feat/EK-910-improve-performance` |

### 智能分析模式

| 偵測到的修改類型 | Branch 前綴 | 示例 |
|----------------|-----------|------|
| Bug Fix | `fix/` | `fix/resolve-login-crash` |
| 新功能 | `feat/` | `feat/add-dark-mode-support` |
| 重構 | `refactor/` | `refactor/network-layer` |
| 效能優化 | `perf/` | `perf/optimize-image-loading` |
| UI/樣式調整 | `style/` | `style/update-button-design` |

## Commit 訊息規則

### Jira 模式
所有 commit 都會自動加上 issue key 前綴：

```
[EK-XXX] {清晰描述修改內容和目的}
```

**好的 commit 訊息示例：**
- `[EK-907] 修改 MainActivity launchMode 為 singleTop 以避免清除上層 Activity`
- `[EK-907] 優化 SplashActivity 重啟邏輯，從 Launcher 啟動時保留 Activity Stack`
- `[EK-908] 添加深色模式支持和主題切換功能`

### 智能分析模式
使用 Conventional Commits 格式：

```
{type}: {清晰描述修改內容和目的}
```

**好的 commit 訊息示例：**
- `fix: 修正 MainActivity launchMode 避免 Activity Stack 被清除`
- `feat: 新增深色模式支持和主題切換功能`
- `refactor: 重構網路層以提升可維護性`
- `perf: 優化圖片載入效能`

**避免的 commit 訊息：**
- ❌ `修改文件` （太模糊）
- ❌ `fix bug` （沒有說明修了什麼）
- ❌ `update code` （缺少類型前綴）

## PR Body 自動生成

### Jira 模式

PR 會自動包含結構化的描述：

```markdown
## 問題描述
{從 Jira description 提取的問題描述}

影響範圍：
- {從 Jira 提取的受影響功能}

## 根本原因分析
{根據代碼修改分析的原因}

## 解決方案
{修改的文件和方法說明}

### Commit 1: {描述}
- 修改文件：{file path}
- 修改內容：{說明}

### Commit 2: {描述}
- 修改文件：{file path}
- 修改內容：{說明}

## 測試場景
- [ ] {自動生成的測試項目 1}
- [ ] {自動生成的測試項目 2}

## 相關 Issue
- Jira: [EK-XXX](https://showyouapp.atlassian.net/browse/EK-XXX)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

### 智能分析模式

PR 會根據程式碼分析自動生成：

```markdown
## 修改描述
{從程式碼修改智能分析出的描述}

影響範圍：
- {分析出的受影響功能/模組}

## 主要變更

### Commit 1: {描述}
- 修改文件：{file path}
- 修改內容：{說明修改的原因和內容}

### Commit 2: {描述}
- 修改文件：{file path}
- 修改內容：{說明修改的原因和內容}

## 測試場景
- [ ] {根據修改內容生成的測試項目 1}
- [ ] {根據修改內容生成的測試項目 2}

## 技術細節
{如有必要，說明重要的技術實作細節}

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

## 進階用法

### 自定義部分 Commit

如果你想要更精細的控制某些 commit：

```bash
# 先手動 stage 特定文件
git add app/src/main/AndroidManifest.xml

# 執行 skill，它會：
# 1. 發現已 staged 的文件，為它們創建一個 commit
# 2. 自動處理剩餘的未 staged 修改
/jira-pr EK-907  # Jira 模式
/jira-pr         # 智能分析模式
```

### 處理多個相關 Issue（Jira 模式）

如果一個 PR 修復了多個相關 issue：

```bash
# 使用主要的 issue
/jira-pr EK-907

# 然後手動在 PR 描述中添加其他 issue 引用
```

### 混合使用兩種模式

你也可以先使用智能分析模式創建 PR，之後再手動在 PR 描述中添加 Jira issue 連結：

```bash
# 先用智能分析快速創建 PR
/jira-pr

# 創建完成後，如果需要可以手動編輯 PR 描述添加 Jira 連結
```

## 故障排除

### Q: Skill 無法執行

**解決方案：**
1. 確認文件在 `.claude/skills/jira-pr/SKILL.md`
2. 重啟 Claude Code
3. 檢查 YAML frontmatter 格式正確（`---` 開頭和結尾）

### Q: Jira 連接失敗

**解決方案：**
```bash
# 檢查 Jira MCP server 配置
# 應該在 .claude/settings.local.json 中有 JIRA_EMAIL 和 JIRA_API_TOKEN
```

### Q: GitHub PR 創建失敗

**解決方案：**
```bash
# 確認 gh CLI 已登入
gh auth status

# 如未登入
gh auth login
```

### Q: Git 衝突或 branch 已存在

**解決方案：**
我會自動檢測並提示你：
- 如果 branch 已存在，會詢問是否覆蓋或使用新名稱
- 如果有未提交的修改衝突，會先提示你處理

### Q: Jira MCP 工具調用失敗

**常見原因：**
- Jira MCP server 未正確配置
- 沒有權限執行 transition 或更新 assignee
- Issue key 不存在或格式錯誤

**解決方案：**
1. **檢查 MCP 連接**：
   ```bash
   # 使用 /mcp 命令檢查 Jira MCP server 狀態
   /mcp
   ```

2. **驗證工具可用性**：
   - 確認 `mcp__jira-extended__` 前綴的工具可用
   - 測試基本操作（如獲取 transitions）

3. **檢查權限**：
   - 確認你的 Jira 帳號有權限轉換 issue 狀態
   - 確認你的帳號有權限修改 assignee 和添加評論

**Jira MCP 工具使用範例**：
```javascript
// 1. 獲取可用的狀態轉換
mcp__jira-extended__jira_get_transitions({ issueKey: "EK-1005" })

// 2. 轉換狀態（使用 transition ID）
mcp__jira-extended__jira_transition_issue({
  issueKey: "EK-1005",
  transitionId: "41"  // QA 測試的 ID
})

// 或使用 transition 名稱
mcp__jira-extended__jira_transition_issue({
  issueKey: "EK-1005",
  transitionName: "QA 測試"
})

// 3. 更新 assignee
mcp__jira-extended__jira_update_issue({
  issueKey: "EK-1005",
  fields: { assignee: { accountId: "712020:..." } }
})

// 4. 添加評論
mcp__jira-extended__jira_add_comment({
  issueKey: "EK-1005",
  comment: "PR 已創建並準備合併至 dev branch: [PR #110](https://github.com/SHOW-YOU-APP/ekkorn-android/pull/110)，修改版本為 102000006"
})
```

**重要提醒**：
- ✅ **統一使用 Jira MCP 工具**（`mcp__jira-extended__*`）
- ✅ 所有 Jira 操作都透過 MCP 完成，不使用 REST API
- ✅ MCP 工具會自動處理認證和錯誤

## 配置

預設配置（可在執行時根據情況調整）：

### 通用配置
- **Base Branch**: `dev`
- **PR Base**: `dev` **（必須，不可更改）**
- **Branch 前綴**: 根據修改類型自動決定（`fix/`、`feat/`、`refactor/` 等）

### Jira 模式配置
- **Commit 前綴**: `[EK-XXX]`
- **完成後動作**:
  - 將 Jira issue 狀態改為 "QA 測試"
  - 將 assignee 改為與 reporter 相同
  - 在 issue 留言說明 PR 連結和修改版本號（從 QA branch 讀取 appVersionCode + 1）

### 智能分析模式配置
- **Commit 格式**: Conventional Commits（`type: description`）
- **分析內容**:
  - Git diff 分析所有修改的檔案
  - Git log 學習專案的 commit 風格
  - 程式碼結構分析（Activity、Fragment、ViewModel 等）
  - 修改意圖推斷（bug fix、feature、refactor 等）

## 相關文檔

- [完整說明文檔](../README.md)
- [快速開始指南](../QUICKSTART.md)

## 技術實現細節

此 skill 使用以下工具和 API：

### Jira 模式
1. **Jira MCP Server (`jira-extended`)** - 完整的 Jira 整合
   - 獲取 issue 資訊
   - 更新狀態、assignee、添加評論
   - 可用工具：
     - `mcp__jira-extended__jira_get_transitions` - 獲取可用的狀態轉換
     - `mcp__jira-extended__jira_transition_issue` - 轉換 issue 狀態
     - `mcp__jira-extended__jira_update_issue` - 更新 issue 欄位（包括 assignee）
     - `mcp__jira-extended__jira_add_comment` - 添加評論
     - `mcp__jira-extended__jira_update_assignee` - 更新受託人
   - **所有 Jira 操作統一使用 MCP 工具**：更安全、更可靠，自動處理認證
2. **Git Commands** - branch 管理、commit、push
3. **GitHub CLI (gh)** - 創建 Pull Request
4. **智能文件分組邏輯** - 根據文件路徑和修改內容自動分組

### 智能分析模式
1. **Git Analysis**:
   - `git status` - 檢查修改狀態
   - `git diff` - 分析具體修改內容
   - `git log` - 學習專案的 commit 風格
2. **Code Analysis**:
   - 檔案類型識別（Activity、Fragment、ViewModel、Repository 等）
   - 修改模式識別（新增功能、修復 bug、重構等）
   - 影響範圍分析（UI、業務邏輯、資料層等）
3. **AI-Powered**:
   - 自然語言生成 PR 描述
   - 智能摘要修改內容
   - 推斷修改意圖和目的
4. **Git Commands** - branch 管理、commit、push
5. **GitHub CLI (gh)** - 創建 Pull Request

### 智能分析邏輯

當使用智能分析模式時，系統會：

1. **收集資訊**：
   - 讀取所有修改的檔案內容
   - 分析修改的行數和位置
   - 識別新增、修改、刪除的函數和類別

2. **推斷意圖**：
   - 如果修改包含 bug fix 關鍵字或異常處理 → Bug Fix
   - 如果新增了類別或功能 → Feature
   - 如果主要是程式碼重組 → Refactor
   - 如果優化了效能 → Performance

3. **生成描述**：
   - 根據修改的檔案和內容生成簡潔的摘要
   - 列出主要變更點
   - 推測可能的測試場景

所有操作都是自動化的，**Jira 模式**需要提供 issue 標識符，**智能分析模式**則完全自動分析。
