# Review PR - 快速開始

## 使用方式

```bash
/review-pr 123                    # PR 編號
/review-pr 123 EK-1005            # PR 編號 + Jira Issue
/review-pr https://github.com/SHOW-YOU-APP/ekkorn-android/pull/123
```

## 流程

1. 獲取 PR 資訊 + diff + 現有 comments
2. 提取 Jira Issue 需求（自動或指定）
3. 已修復的 comments 自動 resolve
4. Code Review：找出嚴重/中等問題
5. 寫入 PR 行內 comments
6. APPROVE 時自動 squash merge
7. 輸出 Review 摘要
