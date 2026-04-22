# 快速開始：create-pr

## 使用方式

```bash
# Jira 模式（必須提供完整 Jira URL）
/create-pr https://xxx.atlassian.net/browse/EK-907

# 智能分析模式（無參數或非 Jira URL）
/create-pr
/create-pr EK-907    # 不會走 Jira 模式
```

不需要事先 `git add` 或 `git commit`，skill 會自動處理。

## Jira 模式範例

```bash
# 修改完程式碼後執行（提供完整 Jira URL）
/create-pr https://xxx.atlassian.net/browse/EK-907

# 自動執行：
# 1. 從 URL 解析 Jira issue key
# 2. 獲取 Jira issue 資訊
# 3. 創建 branch: fix/EK-907-fix-post-detail-activity-stack
# 4. Commit + Push + 創建 PR 到 dev
# 5. review-pr Self-Review → 修復問題 → push
# 6. 更新 Jira issue 狀態 + 留言 PR 連結
```

## 智能分析模式範例

```bash
# 修改完程式碼後執行（無參數或非 Jira URL）
/create-pr

# 自動執行：
# 1. 分析 git diff 判斷修改類型
# 2. 創建 branch: feat/improve-login-flow
# 3. Commit + Push + 創建 PR 到 dev
# 4. review-pr Self-Review → 修復問題 → push
```
