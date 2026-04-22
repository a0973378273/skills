---
name: release-prod
description: 自動將 QA branch 合併到 release，打上版本 tag，build prod release AAB，並發 PR 到 main。當需要準備 Google Play 正式版本時使用此 skill。
---

# Prod Release 自動化

自動化正式版本發布的完整流程，包括合併 QA 到 release、打版本 tag、build prod release AAB、發 PR 到 main。

## 使用方法

```bash
/prod-release
```

## 功能流程

此 skill 會自動執行以下步驟：

### 1. 前置檢查
- 確認當前工作目錄是否乾淨（無未提交變更）
- 如有未提交變更，執行 `git stash`

### 2. 合併分支
- 切換到 QA branch 並同步遠端（`git pull`）
- 切換到 release branch 並同步遠端（`git pull`），若 release branch 不存在則從 main 建立
- 合併 QA branch 到 release（`git merge QA --no-edit`）
- 如遇衝突，停止並提示使用者手動解決

### 3. 讀取版本資訊
- 讀取 `gradle/libs.versions.toml` 中的版本資訊
- 解析 `appVersionName` 和 `appVersionCode`
- 格式化 tag 名稱：`v{appVersionName}({appVersionCode})`
  - 例如：`v1.2.4(102040010)`

### 4. 打版本 Tag
- 檢查該 tag 是否已存在，若已存在則跳過並提示
- 在 release branch 上打 annotated tag：
  ```bash
  git tag -a "v{appVersionName}({appVersionCode})" -m "Release {appVersionName} ({appVersionCode})"
  ```

### 5. 推送到遠端
- 推送 release branch：`git push origin release`
- 推送 tag：`git push origin "v{appVersionName}({appVersionCode})"`

### 6. Build Prod Release AAB
- 執行 `./gradlew bundleProdRelease`
- 等待 build 完成
- 確認 AAB 檔案已產生

### 7. 發 PR 到 main
- 使用 `gh pr create` 從 release branch 發 PR 到 main branch
- PR 標題：`Release {appVersionName} ({appVersionCode})`
- PR 內容包含版本資訊

### 8. 輸出結果
- 印出 AAB 檔案的完整路徑
- 印出版本資訊和 tag 名稱
- 印出 PR 連結

## 執行過程

```
Step 1: 前置檢查
   ├─ git status（檢查工作目錄）
   └─ git stash（如有未提交變更）

Step 2: 合併分支
   ├─ git checkout QA
   ├─ git pull origin QA
   ├─ git checkout release（不存在則從 main 建立）
   ├─ git pull origin release
   └─ git merge QA --no-edit

Step 3: 讀取版本資訊
   ├─ 讀取 gradle/libs.versions.toml
   ├─ 解析 appVersionName
   └─ 解析 appVersionCode

Step 4: 打版本 Tag
   ├─ 檢查 tag 是否已存在
   └─ git tag -a "v{版本}" -m "Release {版本}"

Step 5: 推送到遠端
   ├─ git push origin release
   └─ git push origin "v{版本}"

Step 6: Build AAB
   ├─ ./gradlew bundleProdRelease
   └─ 確認 AAB 檔案產生

Step 7: 發 PR 到 main
   └─ gh pr create --base main --head release

完成！
```

## 完成後輸出

**重要：輸出格式必須使用清單（不可使用表格），且長路徑使用 code block。**

輸出格式範例：
```
## Prod Release 完成

- **版本**: 1.2.4 (102040010)
- **Tag**: v1.2.4(102040010)
- **Branch**: release
- **AAB 檔案**: `app/build/outputs/bundle/prodRelease/app-prod-release.aab`
- **PR**: release → main PR 連結

接下來請手動上傳 AAB 到 Google Play Console，並 review/merge PR。
```

## 故障排除

### 問題：Git merge 衝突
**解決方案：**
- 手動解決衝突後重新執行 `/prod-release`
- 或先執行 `git merge --abort` 後再試

### 問題：Tag 已存在
**解決方案：**
- 如果 tag 已存在，skill 會跳過打 tag 的步驟並提示使用者
- 如需重新打 tag，需先手動刪除舊 tag

### 問題：Gradle build 失敗
**解決方案：**
- 檢查編譯錯誤並修復
- 確保 Android SDK 已正確安裝
- 執行 `./gradlew clean` 後重試

## 前置條件

### 必需工具
- Git（已配置好 remote）
- Gradle wrapper（`./gradlew`）

### 必需檔案
- `gradle/libs.versions.toml`
- `app/build.gradle.kts`

### 權限要求
- 可以推送到 `origin/release` branch
- 可以推送 tags
- 可以使用 `gh` CLI 建立 PR

## 注意事項

1. **自動推送：** 此 skill 會自動推送 release branch 和 tag 到遠端
2. **合併方向：** QA → release → PR 到 main（確保只有通過 QA 測試的程式碼才會進入 release，再經 PR review 合併到 main）
3. **版本號：** 使用 QA branch 上已設定好的版本號，不會修改版本號
4. **AAB 檔案：** build 完成後，需要手動上傳到 Google Play Console
5. **構建時間：** 完整流程約需 1-3 分鐘（視專案大小而定）
6. **PR：** 自動建立 release → main 的 PR，需要手動 review 並 merge
