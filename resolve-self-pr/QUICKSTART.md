# Resolve Self PR - 快速開始

## 前置條件

1. 已安裝並登入 GitHub CLI：
   ```bash
   gh auth status
   ```

## 基本使用

```bash
# 最簡單的方式 - 提供 PR 編號
/resolve-self-pr 123

# 使用完整 URL
/resolve-self-pr https://github.com/SHOW-YOU-APP/ekkorn-android/pull/123
```

## 會做什麼

1. **進入 Worktree** — 建立隔離環境，checkout PR branch
2. **獲取 PR 資訊 + 未解決 comments** — 並行取得所有資訊
3. **分析 Root Cause** — 逐一分析每個 comment 的問題根因
4. **報告 + 直接修復** — 展示分析結果後直接開始修復，不中斷等待確認
5. **回覆 + Resolve** — 修復後自動回覆 reviewer 並 resolve thread
6. **Push + 退出 Worktree** — push 變更，清理 worktree
7. **輸出摘要** — 顯示完整修復報告

## 常見問題

**Q: 可以只修復部分 comment 嗎？**
A: 可以，在呼叫時指定即可，例如 `/resolve-self-pr 123 只修第 1 和第 3 個`。
