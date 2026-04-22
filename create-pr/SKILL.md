---
name: create-pr
description: 自動創建 PR 到 dev branch，支援 Jira 模式與智能分析模式。創建後使用 review-pr skill 做 Self-Review。當需要創建 PR 時使用此 skill。
---

# 創建 PR

## 使用方式

```bash
/create-pr https://xxx.atlassian.net/browse/EK-907    # Jira 模式（必須提供完整 Jira URL）
/create-pr EK-907                                      # 智能分析模式（非 Jira URL，視為無 Jira 單號）
/create-pr                                              # 智能分析模式（無參數）
```

**判斷規則**：只有參數是完整的 Jira URL（包含 `atlassian.net/browse/`）時才走 Jira 模式，其他情況一律走智能分析模式。

---

## Jira 模式（參數為 Jira URL）

1. 從 URL 解析 Jira issue key
2. `mcp__jira-extended__jira_get_issue` 取得 summary、description、type
3. 建立 Branch：Bug → `fix/EK-XXX-slug`，其他 → `feat/EK-XXX-slug`
4. Commit + Push + 建立 PR（target: `dev`）
5. 使用 `review-pr` skill 審查剛建立的 PR，修復問題後 push
6. `mcp__jira-extended__jira_add_comment`：`PR 已創建並準備合併至 dev branch: [PR #N|URL]`
7. `mcp__jira-extended__jira_transition_issue`，transitionName: `進行中`

## 智能分析模式（無參數或參數非 Jira URL）

1. `git status` + `git diff` + `git log` 分析修改類型和意圖
2. 建立 Branch：`fix/`（bug fix）、`feat/`（功能）、`refactor/`（重構）
3. Commit + Push + 建立 PR（target: `dev`），自動生成描述
4. 使用 `review-pr` skill 審查剛建立的 PR，修復問題後 push

---

## PR 格式

### 標題
- Jira 模式：`[EK-XXX] {summary}`
- 智能模式：`{type}: {摘要}`

### Body
- 問題描述 + 影響範圍
- 根本原因分析（如適用）
- 解決方案（per commit 說明）
- 測試場景 checklist
- 相關 Issue 連結（Jira 模式）
- `🤖 Generated with [Claude Code](https://claude.com/claude-code)`
