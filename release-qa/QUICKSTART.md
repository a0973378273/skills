# QA Release 快速開始

## 🚀 30 秒快速上手

```bash
/qa-release
```

就這麼簡單！

## 📝 完整示例

### 步驟 1: 執行命令
在 Claude Code 中輸入：
```bash
/qa-release
```

### 步驟 2: 自動生成 Release Notes
系統會自動從 dev branch 的 commit 歷史中提取更新內容

### 步驟 3: 等待完成
系統會自動執行：
- ✅ 合併 dev 到 QA
- ✅ 更新版本號（例如：102000020 → 102000021）
- ✅ 更新 release notes
- ✅ Commit 並 push
- ✅ 建置並上傳 APK 到 Firebase

### 步驟 4: 獲取連結
完成後你會收到：
- 🔗 Firebase Console 連結
- 🔗 測試人員下載連結

## 💡 常見用例

### 用例 1: 快速發布修復
```bash
# 1. 在 dev branch 修復 bug 並 commit（包含 Jira issue）
git commit -m "fix: [EK-927] 修復登入問題"

# 2. 發布到 QA（系統會自動提取 [EK-927]）
/qa-release
```

### 用例 2: 發布新功能
```bash
# 1. 開發完成並合併到 dev（使用標準 commit 格式）
git checkout dev
git merge feature/new-dashboard
git commit -m "feat: [EK-930] 新增儀表板功能"

# 2. 發布到 QA（系統會自動生成 Release Notes）
/qa-release
```

### 用例 3: 多項更新（多個 PRs）
```bash
# dev branch 包含多個 PRs：
# PR #126: fix: [EK-927] 修復登入問題
# PR #128: feat: [EK-930] 新增儀表板功能
# PR #130: perf: [EK-932] 改善載入效能

# 執行後會自動整理成 Release Notes
/qa-release

# 輸出：
# - [EK-927] 修復登入問題
# - [EK-930] 新增儀表板功能
# - [EK-932] 改善載入效能
```

### 用例 4: 一個 PR 包含多個 Issues
```bash
# PR #135 包含：
# - feat: [EK-940] 新增訊息通知功能
# - fix: [EK-942] 修正通知音效問題

# 執行後會分別列出兩個 issues
/qa-release

# 輸出：
# - [EK-940] 新增訊息通知功能
# - [EK-942] 修正通知音效問題
```

## ⚡ 快速檢查清單

執行 `/qa-release` 前確認：

- [ ] 所有變更已在 dev branch 完成
- [ ] Dev branch 已推送到遠端
- [ ] Commit 訊息包含 Jira issue 編號（建議格式：`type: [EK-XXX] description`）
- [ ] 你有 QA branch 的推送權限
- [ ] Firebase 配置正確

**提示：** 使用標準 commit 格式可以讓 Release Notes 更清晰易讀

## 🎯 預期結果

### 版本號更新示例

**情況 A - 構建號遞增：**
```
之前: appVersionName = "1.2.3", appVersionCode = "102030001"
之後: appVersionName = "1.2.3", appVersionCode = "102030002"
```

**情況 B - 構建號重置（版本號已更新）：**
```
之前: appVersionName = "1.2.4", appVersionCode = "102030010"
之後: appVersionName = "1.2.4", appVersionCode = "102040001"
```

**情況 C - 主版本多位數：**
```
之前: appVersionName = "10.2.3", appVersionCode = "1002030001"
之後: appVersionName = "10.2.3", appVersionCode = "1002030002"
```

### Release Notes 示例

**自動生成的 Release Notes：**
```
Release Build
建置時間: 2026-01-26 18:18:33
Git Commit: de03b336
Android 版本: 1.2.3 (102030002)

主要更新:
- [EK-927] 調整 tooltip 渲染時機
- [EK-930] 修正登出頁面過渡動畫
- [EK-932] 新增使用者設定頁面
```

**說明：**
- 系統自動從 dev branch 的 commits 中提取
- Jira issue 編號自動識別
- 按照 PR 分組，每個 PR 內不同的 issue 分別列出
- 如果一個 PR 有多個不同的 `[EK-XXX]`，會生成多條 release notes
- 按照 feat > fix > refactor > chore 順序排列

## ❓ 常見問題

### Q: 需要多長時間？
A: 通常 3-5 分鐘，包括建置和上傳時間。

### Q: 可以取消嗎？
A: 在 commit 前可以用 Ctrl+C 取消。Commit 後需要手動回退。

### Q: 上傳失敗怎麼辦？
A: 檢查 Firebase 配置和網路，然後重新執行 `/qa-release`。

### Q: 版本號計算錯誤？
A: 檢查 `gradle/libs.versions.toml` 中的 `appVersionName` 和 `appVersionCode` 是否正確。

## 🔍 驗證發布

執行後訪問 Firebase Console 連結，確認：
- ✅ 版本號正確
- ✅ Release notes 內容正確
- ✅ APK 已分發給測試群組

## 📞 需要幫助？

如果遇到問題：
1. 查看完整文檔：[SKILL.md](./SKILL.md)
2. 檢查錯誤訊息
3. 確認前置條件都已滿足

---

**現在就試試：**
```bash
/qa-release
```
