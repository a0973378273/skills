# Claude Code Skills

這個目錄包含了項目的自定義 Claude Code skills。

## 可用的 Skills

### `/jira-pr` - 智能 PR 創建

自動化創建 Pull Request 的完整流程。支援兩種模式：
- **Jira 模式**：從 Jira issue 獲取資訊（有對應 issue 時使用）
- **智能分析模式**：分析程式碼修改自動生成 PR 描述（無 Jira issue 時使用）

#### 使用方法

Jira 模式（使用完整 URL）：
```bash
/jira-pr https://showyouapp.atlassian.net/browse/EK-907
```

Jira 模式（使用 issue key）：
```bash
/jira-pr EK-907
```

智能分析模式（不提供參數）：
```bash
/jira-pr
```

#### 功能說明

這個 skill 會自動完成以下步驟：

##### Jira 模式

1. **獲取 Jira Issue 資訊**
   - 從提供的 URL 或 Issue Key 獲取 issue 詳情
   - 解析 summary, description, issue type 等資訊

2. **創建 Branch**
   - 從 `dev` branch 創建新的 branch
   - Branch 命名規則：
     - Bug/漏洞：`fix/EK-XXX-{summary-slug}`
     - Feature/其他：`feat/EK-XXX-{summary-slug}`
   - 自動將 summary 轉換為 kebab-case

3. **智能 Commit**
   - 檢查當前的 git 修改
   - 根據修改的文件類型自動分組
   - 每個 commit 格式：`[EK-XXX] {描述}`

4. **創建 Pull Request**
   - 自動 push 到 remote
   - 創建 PR 到 `dev` branch
   - PR 標題：`[EK-XXX] {Jira summary}`
   - PR body 包含問題描述、解決方案、測試場景、Jira issue 連結

5. **更新 Jira Issue**
   - 將 issue 狀態改為 "QA 測試"
   - 更新 assignee
   - 添加 PR 連結評論

##### 智能分析模式

1. **分析程式碼修改**
   - 使用 `git diff` 和 `git status` 分析所有修改
   - 識別修改的檔案類型和意圖
   - 理解修改的目的（bug fix、feature、refactor 等）

2. **智能生成資訊**
   - 自動產生合適的 PR 標題和描述
   - 推斷修改類型（fix/feat/refactor/perf 等）
   - 生成測試場景建議

3. **創建 Branch**
   - 根據修改類型選擇 branch 前綴
   - 自動產生語義化的 branch 名稱

4. **智能 Commit**
   - 使用 Conventional Commits 格式
   - 根據檔案類型自動分組
   - 每個 commit 格式：`{type}: {描述}`

5. **創建 Pull Request**
   - 自動 push 到 remote
   - 創建 PR 到 `dev` branch，包含智能生成的完整描述

#### 示例

##### 示例 1：Jira 模式

假設你修改了以下文件來修復 EK-907：
- `app/src/main/AndroidManifest.xml`
- `app/src/main/java/.../MainActivity.kt`
- `app/src/main/java/.../SplashActivity.kt`

執行：
```bash
/jira-pr EK-907
```

會自動創建：
- Branch: `fix/EK-907-fix-post-detail-activity-stack-on-resume`
- Commits:
  1. `[EK-907] 修改 MainActivity launchMode 為 singleTop 以避免清除上層 Activity`
  2. `[EK-907] 優化 SplashActivity 重啟邏輯，從 Launcher 啟動時保留 Activity Stack`
- PR: https://github.com/SHOW-YOU-APP/ekkorn-android/pull/110
- 自動更新 Jira issue 狀態和添加評論

##### 示例 2：智能分析模式

假設你優化了登入流程，修改了：
- `app/src/main/java/.../LoginViewModel.kt`
- `analytics/src/main/java/.../AFTracker.kt`
- `app/src/main/java/.../NewcomerBonusBanner.kt`

執行：
```bash
/jira-pr
```

會自動創建：
- Branch: `feat/improve-login-newcomer-banner-and-tracking`
- Commits:
  1. `feat: 優化 LoginViewModel 新手引導橫幅的顯示條件`
  2. `feat: 新增 AFTracker 登入流程事件追蹤`
  3. `feat: 改善 NewcomerBonusBanner UI 顯示效果`
- PR 包含完整的自動生成描述，無需 Jira issue

#### 前置條件

##### 通用前置條件（兩種模式都需要）
- 確保當前在 git repository 中
- 確保有未提交的修改
- 確保有 GitHub 訪問權限（已安裝 `gh` CLI）

##### Jira 模式額外需要
- 確保有 Jira 訪問權限（已配置 MCP server）

##### 智能分析模式
- 不需要 Jira 連接
- 會自動分析程式碼修改來生成 PR 內容

#### 配置

##### Jira 模式
- 目標 branch：`dev`
- Commit 訊息前綴：`[EK-XXX]`
- Branch 前綴：`fix/` 或 `feat/`（根據 issue type）

##### 智能分析模式
- 目標 branch：`dev`
- Commit 格式：Conventional Commits（`type: description`）
- Branch 前綴：根據修改類型自動選擇（`fix/`、`feat/`、`refactor/`、`perf/` 等）

## 如何創建新的 Skill

在 `.claude/skills/` 目錄下創建新的 JSON 文件：

```json
{
  "name": "my-skill",
  "description": "簡短描述",
  "instructions": "詳細的執行指令和說明"
}
```

然後在 Claude Code 中使用：

```bash
/my-skill [參數]
```

## 疑難排解

### Skill 無法執行

1. 檢查 skill 文件格式是否正確
2. 重啟 Claude Code
3. 確認文件在正確的目錄：`.claude/skills/`

### Jira 連接失敗

確認 MCP server 配置正確：
```bash
# 檢查 Jira MCP server 狀態
# 應該在 Claude Code 啟動時自動連接
```

### PR 創建失敗

確認 GitHub CLI 已登入：
```bash
gh auth status
```

如果未登入：
```bash
gh auth login
```
