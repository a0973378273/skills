---
name: resolve-self-pr
description: 解析自己 PR 上 reviewer 的 comments，分析 root cause、提出解決方案並實作修復。修復後自動回覆 reviewer、resolve 已修復的 thread，並 push commit。適合用於處理自己 PR 被 review 後的修復工作。
---

# Resolve Self PR

自動化處理自己 PR 上的 review comments。解析 reviewer 的 comments，分析 root cause 並修復。

## 快速使用

使用 PR URL：
```bash
/resolve-self-pr https://github.com/SHOW-YOU-APP/ekkorn-android/pull/123
```

使用 PR 編號：
```bash
/resolve-self-pr 123
```

## 執行流程

### 0. 進入 Worktree 隔離環境

**重要：在進行任何程式碼修改之前，必須先進入 worktree 隔離環境。**

1. 使用 `EnterWorktree` 工具建立隔離的 git worktree
2. 在 worktree 中 checkout PR 的 branch：
   ```bash
   git checkout {PR 的 head branch}
   git pull origin {PR 的 head branch}
   ```
3. 後續所有的程式碼分析、修改、commit、push 都在此 worktree 中進行
4. 修復完成後，使用 `ExitWorktree` 離開並清理 worktree

**原因：** 避免影響當前工作目錄中正在進行的其他工作。

### 1. 獲取 PR 資訊與未解決的 Review Comments

一次性取得所有需要的資訊，以下指令**並行執行**：

```bash
# 獲取 PR 基本資訊（標題、branch 等）
gh pr view {number} --json title,body,headRefName,baseRefName,url,number

# 獲取所有 review comments
gh api repos/{owner}/{repo}/pulls/{number}/comments

# 獲取 review threads（用於判斷 resolved 狀態）
gh api repos/{owner}/{repo}/pulls/{number}/reviews
```

從 comments 中篩選出**未 resolved** 且**非自己發的** comments，按檔案分組整理。

### 2. 分析每個 Comment 的 Root Cause

對每個未解決的 comment：

1. **理解 reviewer 的意圖**：解析 comment 內容，判斷指出的問題類型（邏輯錯誤、效能、安全、架構等）
2. **定位相關程式碼**：讀取 comment 標記的檔案和行號，以及周圍的上下文
3. **追蹤呼叫鏈**：如需要，使用 `Grep` 和 `Read` 追蹤相關的程式碼路徑
4. **分析 root cause**：找出問題的根本原因

### 3. 報告分析結果並直接修復

以結構化的方式展示分析結果，**然後直接開始修復，不等待使用者確認**：

```
🔍 PR Review Comments 分析: #{PR 編號}

📝 Comment 1 - by {reviewer} ({檔案}:{行號})
  💬 原始 comment: {comment 內容摘要}
  🎯 Root Cause: {根本原因分析}
  🔧 修復方式: {具體的修復方案}

📝 Comment 2 - by {reviewer} ({檔案}:{行號})
  💬 原始 comment: {comment 內容摘要}
  🎯 Root Cause: {根本原因分析}
  🔧 修復方式: {具體的修復方案}

...

開始修復...
```

### 4. 實作修復、回覆並 Resolve

依序修復每個問題，每個修復完成後立即：

1. **Commit** 修改
2. **回覆** 對應的 review comment
3. **Resolve** 該 thread

回覆格式：

- **已修復的 comment**：
  ```
  已修復：{簡短說明做了什麼改動}
  ```
- **跳過的 comment**：
  ```
  已知悉，{跳過原因}
  ```
- **無法修復的 comment**：回覆說明情況並尋求討論

回覆 API：
```bash
gh api repos/{owner}/{repo}/pulls/{number}/comments/{comment_id}/replies \
  --method POST \
  -f body="已修復：{說明}"
```

Resolve API（GraphQL）：
```bash
gh api graphql -f query='
  mutation {
    resolveReviewThread(input: {threadId: "{thread_id}"}) {
      thread { isResolved }
    }
  }
'
```

全部修復完成後，一次性 push：
```bash
git push origin {branch}
```

### 5. 退出 Worktree

- 使用 `ExitWorktree` 離開 worktree
- 選擇 **remove** 清理 worktree（因為變更已 push 到 remote）

### 6. 產出修復摘要

```
📋 PR Comments 修復摘要: #{PR 編號} {PR 標題}

🔄 未解決的 Comments ({N} 個):

✅ 已修復 ({M} 個):
1. {檔案}:{行號} - {問題摘要} → {修復方式}
2. ...

⏭️ 跳過 ({K} 個):
1. {檔案}:{行號} - {原因}
2. ...

❓ 待討論 ({J} 個):
1. {檔案}:{行號} - {需要與 reviewer 討論的問題}
2. ...

🔗 PR 連結: {PR URL}
```

## 參數說明

| 參數 | 類型 | 必填 | 說明 | 示例 |
|-----|------|------|------|------|
| PR URL/編號 | String | 必填 | PR 的 URL 或編號 | `123` 或 `https://github.com/.../pull/123` |

## 技術實現細節

此 skill 使用以下工具和 API：

### GitHub API（透過 gh CLI）

1. **獲取 PR 資訊**：
   ```bash
   gh pr view {number} --json title,body,headRefName,baseRefName,url,number
   ```

2. **獲取現有 Review Comments**：
   ```bash
   gh api repos/{owner}/{repo}/pulls/{number}/reviews
   gh api repos/{owner}/{repo}/pulls/{number}/comments
   ```

3. **回覆 PR Review Comment**：
   ```bash
   gh api repos/{owner}/{repo}/pulls/{number}/comments/{comment_id}/replies \
     --method POST \
     -f body="已修復：{說明}"
   ```

4. **Resolve Review Thread（GraphQL）**：
   ```bash
   gh api graphql -f query='
     mutation {
       resolveReviewThread(input: {threadId: "{thread_id}"}) {
         thread { isResolved }
       }
     }
   '
   ```

### 程式碼分析

- 使用 `Read` 工具讀取完整檔案（需要更多上下文時）
- 使用 `Grep` 搜尋相關程式碼（追蹤呼叫鏈時）

## 前置條件

執行此 skill 前請確保：

- ✅ 已安裝並登入 `gh` CLI（GitHub CLI）
- ✅ 有 PR 的讀寫權限

## 故障排除

### Q: 無法獲取 PR 資訊

**解決方案：**
```bash
# 確認 gh CLI 已登入
gh auth status

# 確認有權限存取 repository
gh repo view
```

### Q: 回覆 Comment 失敗

**解決方案：**
- 確認有 PR 的寫入權限
- 確認 comment ID 正確（部分 review body comment 無法直接回覆）

### Q: Resolve 失敗

**解決方案：**
- 確認有 thread ID（需透過 GraphQL 查詢取得）
- 確認有 resolve 的權限

## 配置

預設行為：

- **Comment 語言**: 繁體中文
- **Resolve 策略**: 修復後自動 resolve
- **目標 Repo**: `SHOW-YOU-APP/ekkorn-android`（從 git remote 自動偵測）
