---
name: do-jira-task
description: 從 Jira issue 自動分析需求、列出 TODO 清單並依序完成任務。會主動提出需要確認的問題和缺少的資源。適合用於實作新功能、修復 bug 或任何需要完整執行的 Jira 任務。
---

# Jira 任務自動實作

## 快速使用

```bash
/do-jira-task EK-907                # Issue Key
/do-jira-task https://showyouapp.atlassian.net/browse/EK-907  # 完整 URL
/do-jira-task EK-907 21:00          # 排程執行（CronCreate）
```

## 排程執行

若提供時間參數（如 `21:00`、`at 9pm`），使用 `CronCreate` 建立排程，不立即執行。

## 執行流程

### 1. 獲取並分析 Jira Issue
- 使用 `mcp__jira-extended__jira_get_issue` 獲取 summary、description、type、priority、comments
- 識別缺少的資源（設計圖、API 規格、素材）並主動提問

### 2. Root Cause 分析（Bug 類型必做）
- 用 Grep + Read 追蹤執行路徑，定位根本原因（非表面現象）
- 記錄分析結果供最終摘要使用，直接進入下一步不等確認
- 3 輪分析找不到原因就回報假說 + 採用最可能方案繼續

### 3. 建立 Worktree
1. `git fetch origin dev`
2. `EnterWorktree`（name 用分支名）
3. `git reset --hard origin/dev`
4. 分支命名：Bug → `fix/EK-XXXX-描述`，其他 → `feat/EK-XXXX-描述`
5. Fallback：`git checkout -b <branch> origin/dev`

### 4. 創建 TODO 清單並依序執行
- 使用 TaskCreate 建立任務，TaskUpdate 更新狀態
- 按序完成，遇問題暫停詢問

### 5. 完成與驗證
- Bug 類型必須輸出 Root Cause 摘要：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 Root Cause 摘要
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 問題描述：[描述]
🎯 根本原因：[root cause]
📁 涉及位置：[檔案:行號]
🔧 修復方案：[方案說明]
🧪 驗證步驟：[步驟列表]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6. 安裝驗證循環

此步驟為**無限循環**，直到驗證成功並建立 PR 後才結束。

#### 6a. 詢問是否安裝驗證（使用 AskUserQuestion）
1. **安裝到裝置驗證**
2. **跳過安裝，直接建立 PR**
3. **結束流程（不建立 PR）**

#### 6b. 選擇 1 → 安裝驗證
- `./gradlew installQaDebug`
- 啟動：`adb shell am start -n com.showyouapp.ekkorn/com.work.xux.want.presentation.feature.splash.SplashActivity`
- 安裝完成後，詢問驗證結果（使用 AskUserQuestion）：
  1. **驗證成功，建立 PR**
  2. （使用者直接輸入失敗情況描述）

##### 選擇 1 → 驗證成功
- 呼叫 `/create-jira-pr-reviewer` 建立 PR → `ExitWorktree(action: "remove")` → **流程結束**

##### 使用者輸入失敗情況 → 繼續解題
- 根據使用者描述的問題，在**當前 Worktree 中**繼續分析並修復
- 修復完成後 → **回到步驟 6a**，再次詢問是否安裝驗證
- 此循環持續到使用者驗證成功為止

#### 6c. 選擇 2 → 跳過安裝
- 直接呼叫 `/create-jira-pr-reviewer` 建立 PR → `ExitWorktree(action: "remove")` → **流程結束**

#### 6d. 選擇 3 / Esc / /clear → 直接結束
- `ExitWorktree(action: "remove")` → **流程結束**（不建立 PR）

**重要**：
- 每次修復後都要重新詢問安裝選擇，不可直接執行安裝或跳過
- 驗證失敗時不需要 ExitWorktree，在當前 Worktree 中繼續修復
- 使用者在任何詢問階段選擇 3、按 Esc、或 /clear，都直接 ExitWorktree 結束
- 只有驗證成功建立 PR 後、選擇跳過建立 PR 後、或使用者主動結束後，流程才算結束
