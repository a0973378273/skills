---
name: review-pr
description: Review PR 連結，根據 Jira issue 需求檢查實作是否正確，將嚴重與中等問題寫為 PR 行內 comment，並自動 resolve 已修復的 comment。適合用於 Code Review、PR 審查時使用。
---

# PR Code Review

審查 PR，寫 review comments。參數：`PR URL 或編號` + 可選 `Jira Issue Key`。

## 執行流程

### 0. 解析 Repo 與 PR 編號

從使用者傳入的參數解析 `{owner}/{repo}` 和 `{number}`：
- **完整 URL**（如 `https://github.com/SHOW-YOU-APP/ekkorn-ios/pull/123`）→ 提取 `SHOW-YOU-APP/ekkorn-ios` 和 `123`
- **純數字**（如 `123`）→ 預設使用當前目錄的 git remote（`gh repo view --json nameWithOwner -q .nameWithOwner`），若失敗則 fallback 到 `SHOW-YOU-APP/ekkorn-android`

以下所有命令中的 `{owner}/{repo}` 均來自此步驟解析結果。

### 1. 獲取 PR 資訊（並行執行）

同時執行以下命令以減少 round-trip：
- `gh pr view {number} --repo {owner}/{repo} --json title,body,headRefName,baseRefName,url,number`
- `gh pr diff {number} --repo {owner}/{repo}`
- `gh api repos/{owner}/{repo}/pulls/{number}/reviews --jq '[.[] | {id, user: .user.login, state: .state}]'`
- `gh api repos/{owner}/{repo}/pulls/{number}/comments --jq '[.[] | {id, path, line, body, user: .user.login, in_reply_to_id}]'`

### 2. 獲取 Jira Issue（如適用）

從 PR 標題/描述提取 `EK-XXX`（或使用者指定的 key），用 `mcp__jira-extended__jira_get_issue` 取得 summary、description、issue type。無 Jira Key 則跳過需求比對。

### 3. Resolve 已修復的 Comments

用 GraphQL 取得 review threads：
```bash
gh api graphql -f query='query { repository(owner:"{owner}",name:"{repo}") { pullRequest(number:{N}) { reviewThreads(first:100) { nodes { id isResolved comments(first:10) { nodes { body author { login } } } } } } } }'
```

對每個由我發出的未 resolved thread，判斷是否應 resolve：
- **應 resolve**：程式碼已修改/刪除修復了問題、或開發者已回覆確認（解釋設計意圖、確認預期行為等）
- **不 resolve**：問題仍存在且無實質回覆、或開發者僅說「我看看」無結論

Resolve 用：
```bash
gh api graphql -f query='mutation { resolveReviewThread(input:{threadId:"{id}"}) { thread { isResolved } } }'
```

### 4. Code Review 分析

讀取原始碼時**只讀 diff 涉及的行數範圍**（用 `Read` 的 `offset`/`limit`），不要讀整個檔案。需要追蹤呼叫鏈時才用 `Grep`。

#### 嚴重問題（Critical） — 寫 comment
- 邏輯錯誤（crash、功能異常）
- 安全漏洞、資源/記憶體洩漏
- 線程安全（錯誤線程操作 UI、race condition）
- 資料一致性問題

#### 中等問題（Medium） — 寫 comment
- 效能問題、錯誤處理不足
- 架構違規（MVI/MVVM）、scope 使用不當
- 邊界條件、硬編碼值

#### 輕微問題 — 僅在摘要中提及，不寫 comment
- 命名不一致、風格問題、可改進但不影響功能的寫法

### 5. 提交 PR Review

一次提交所有 comments（避免大量通知）：
```bash
gh api repos/{owner}/{repo}/pulls/{number}/reviews \
  --method POST \
  --field body="{summary}" \
  --field event="{APPROVE|COMMENT|REQUEST_CHANGES}" \
  --field 'comments=[{"path":"file.kt","line":42,"side":"RIGHT","body":"comment"}]'
```

Comment 格式：
```
**[嚴重/Critical]** 或 **[中等/Medium]**
{問題描述}
{為什麼這是問題}
建議修改：{具體建議或程式碼}
```

Review 類型判定：
- 有嚴重問題 → `REQUEST_CHANGES`
- 僅中等問題 → `COMMENT`
- 無嚴重/中等問題 → `APPROVE`

### 6. Auto-merge（僅 APPROVE）

APPROVE 後自動 merge（使用 merge commit）：
```bash
gh pr merge {number} --merge --repo {owner}/{repo}
```
然後用 `gh pr view {number} --repo {owner}/{repo} --json state,mergedAt` 確認狀態。失敗則回報原因。

### 7. 輸出摘要

```
PR Review 摘要: #{number} {title}

Jira Issue: EK-XXX - {title}（如有）

需求符合度:（如有 Jira）
- {已實作/未實作的需求}

嚴重問題 ({N} 個):
1. {file}:{line} - {摘要}

中等問題 ({N} 個):
1. {file}:{line} - {摘要}

輕微建議 ({N} 個):
1. {摘要}

已 Resolve 的 Comments ({N} 個):
1. {file}:{line} - {原問題} — {resolve 原因}

總結: {整體評價}

合併狀態: 已合併 / 合併失敗（原因）/ 未合併（非 APPROVE）

PR 連結: {url}
```
