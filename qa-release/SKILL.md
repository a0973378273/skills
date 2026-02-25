---
name: qa-release
description: 自動將 dev branch 合併到 QA branch、更新版本號、修改 release notes 並上傳到 Firebase App Distribution。當需要發布 QA 版本時使用此 skill。
---

# QA Release 自動化

自動化 QA 版本發布的完整流程，包括合併分支、版本號管理、release notes 更新和 Firebase 部署。

## 使用方法

```bash
/qa-release
```

執行後會自動從 dev branch 的 commit 歷史中提取 Release Note。

## 功能流程

此 skill 會自動執行以下步驟：

### 1. 合併分支
- Stash 當前變更（如有）
- 切換到 dev branch 並同步遠端（git pull）
- 切換到 QA branch
- 合併 dev branch 到 QA

### 2. 自動生成 Release Notes
- 查詢 QA branch 與 dev branch 之間的差異 commit
- 從 commit 訊息中提取資訊：
  - Jira issue 編號（如 [EK-XXX]、EK-XXX）
  - 功能描述（fix、feat、chore 等）
  - PR 標題和描述
- 自動整理成 Release Note 列表

### 3. 版本號管理
- 讀取 `gradle/libs.versions.toml` 中的版本資訊
- 解析 `appVersionName` 和 `appVersionCode`
- 根據版本號規則自動更新：
  - 如果 `appVersionCode` 前五位與 `appVersionName` 對應值相同：後四位數字 +1
  - 如果不同：前五位更新為與 `appVersionName` 對應值，後四位重置為 0001

**版本號格式：**
- `appVersionCode` = 主版本(可變位數) + 次版本(2位) + 修訂版本(2位) + 構建號(4位)
- 例如：
  - `102030001` = 1(主版本) + 02(次版本) + 03(修訂版本) + 0001(構建號) [9位數]
  - `1002030001` = 10(主版本) + 02(次版本) + 03(修訂版本) + 0001(構建號) [10位數]
- 版本號對應規則：
  - 主版本：與 `appVersionName` 第一個數字相同（可為多位數，如 10、100）
  - 次版本（2位）：與 `appVersionName` 第一個 `.` 後數字相同（0-9 時左側補 0）
  - 修訂版本（2位）：與 `appVersionName` 第二個 `.` 後數字相同（0-9 時左側補 0）
  - 構建號（4位）：版本號未變時遞增，版本號改變時重置為 0001

### 4. 更新 Release Notes
- 修改 `app/build.gradle.kts` 中 `createReleaseNotes` 任務的「主要更新:」內容
- 使用步驟 2 自動生成的 Release Note 列表

### 5. 提交變更
- Git add 版本檔案
- 創建 commit（包含版本號和更新內容）
- Push 到遠端 QA branch

### 6. Firebase App Distribution 部署
- 執行 `./gradlew uploadQaRelease`
- 自動建置 QA release APK
- 上傳到 Firebase App Distribution
- 分發到 Dev 和 QA 測試群組

### 7. Jira Issue 驗證與修正
Firebase 部署完成後，自動驗證此版本涉及的所有 Jira issue 狀態是否正確，若不符合則自動修正。

**驗證項目：**

#### 7.1 狀態檢查
- 使用 `mcp__jira-extended__jira_get_issue` 取得每個 issue 的當前狀態
- 確認狀態是否為「QA 測試」
- 若不是，使用 `mcp__jira-extended__jira_transition_issue` 將狀態改為「QA 測試」

#### 7.2 受託人檢查
- 確認 issue 的 assignee（受託人）是否為 reporter（回報人）
- 若不是，使用 `mcp__jira-extended__jira_update_assignee` 將 assignee 改為 reporter

#### 7.3 留言檢查
- 取得 issue 的最新留言
- 確認最新留言是否包含：
  - 此次發布的版號（新的 `appVersionCode`）
  - 對應的 PR 連結（從 git log 中提取的 PR 號碼和 URL）
- 若最新留言不包含以上資訊，使用 `mcp__jira-extended__jira_add_comment` 添加留言
- 留言格式：「QA 版本已發布，版號：{appVersionCode}，相關 PR：[PR #{PR_NUMBER}]({PR_URL})」

**PR 連結提取規則：**
- 從 `git log QA..dev` 的 merge commit 中提取 PR 號碼
- 將每個 Jira issue 與對應的 PR 進行匹配（根據 commit 訊息中的 `[EK-XXX]` 或 `EK-XXX`）
- PR URL 格式：`https://github.com/SHOW-YOU-APP/ekkorn-android/pull/{PR_NUMBER}`

**驗證結果輸出：**
```
📋 Jira Issue 驗證結果：
- [EK-927] ✅ 狀態: QA 測試 | ✅ 受託人: 回報人 | ✅ 留言: 已包含版號和 PR 連結
- [EK-930] ⚠️ 狀態: 已修正→QA 測試 | ✅ 受託人: 回報人 | ⚠️ 留言: 已補充版號和 PR 連結
- [EK-932] ✅ 狀態: QA 測試 | ⚠️ 受託人: 已修正→回報人 | ✅ 留言: 已包含版號和 PR 連結
```

## 執行示例

```bash
# 啟動 QA release 流程
/qa-release
```

**自動化流程：**
1. 自動從 dev branch 的 commit 歷史提取更新內容
2. 識別 Jira issue（如 EK-927、EK-930）和功能描述
3. 自動生成 Release Note 並執行所有步驟

**Release Note 範例：**
```
主要更新:
- [EK-927] 調整 tooltip 渲染時機
- [EK-930] 修正登出頁面過渡動畫
- [EK-932] 新增使用者設定頁面
```

## 完成後輸出

執行成功後會提供：
- ✅ 自動生成的 Release Note 列表
- ✅ 版本更新資訊（舊版本 → 新版本）
- ✅ Firebase Console 管理連結
- ✅ 測試人員下載連結
- ✅ Git commit 資訊
- ✅ Jira Issue 驗證與修正結果（狀態、受託人、留言）

**重要：提供以下正確的 Firebase 連結**
- Firebase 專案 ID: `show-you-8f297`
- Package Name: `com.showyouapp.ekkorn`
- Firebase Console (App Distribution): `https://console.firebase.google.com/project/show-you-8f297/appdistribution/app/android:com.showyouapp.ekkorn`
- Firebase Console (專案總覽): `https://console.firebase.google.com/project/show-you-8f297/appdistribution`

## Release Note 自動生成規則

此 skill 會自動從 dev branch 的 commit 歷史中提取更新內容，生成 Release Note。

### 提取來源
使用 `git log QA..dev` 來查詢從 QA 到 dev 之間新增的所有 commits。

### 識別規則

#### 1. 識別 PR/Branch Merge
從 merge commit 識別 PR：
```
Merge pull request #126 from SHOW-YOU-APP/fix-ring-tooltip
→ PR #126，接下來分析此 PR 內的所有 commits
```

#### 2. 提取 Jira Issue 編號
從 PR 內的 commits 提取所有不同的 Jira issues：
- 格式：`[EK-XXX]`、`EK-XXX`
- 範例：
  ```
  PR #126 包含：
    ├─ fix: [EK-927] adjust tooltip rendering timing
    ├─ fix: [EK-927] update tests
    └─ test: [EK-927] add test cases

  → 提取：[EK-927]（只有一個 issue）
  → Release Note: [EK-927] adjust tooltip rendering timing
  ```

  ```
  PR #130 包含：
    ├─ feat: [EK-930] add user settings page
    ├─ fix: [EK-932] fix logout animation
    └─ feat: [EK-930] add validation

  → 提取：[EK-930]、[EK-932]（兩個不同的 issues）
  → Release Note:
    - [EK-930] add user settings page
    - [EK-932] fix logout animation
  ```

#### 3. 功能描述提取
從每個不同的 issue 中選取第一個有意義的描述：
- `fix:` - 修復問題
- `feat:` - 新增功能
- `chore:` - 維護更新
- `refactor:` - 重構代碼
- `docs:` - 文件更新
- `test:` - 測試更新

#### 4. 處理沒有 PR 的直接 commits
如果某些 commits 不屬於任何 PR（直接 commit 到 dev）：
```
直接 commit: fix: [EK-935] hotfix for crash issue
→ Release Note: [EK-935] hotfix for crash issue
```

### 生成格式

**基本格式：**
```
主要更新:
- [EK-XXX] 簡短描述
- [EK-YYY] 簡短描述
- 其他更新描述
```

**完整範例：**

假設有以下 PRs 合併到 dev：
```
PR #126: fix-tooltip
  └─ fix: [EK-927] adjust tooltip rendering timing

PR #128: logout-improvements
  ├─ fix: [EK-930] fix logout animation
  └─ test: [EK-930] add logout tests

PR #130: multi-feature
  ├─ feat: [EK-932] add user settings page
  ├─ fix: [EK-935] fix settings validation
  └─ feat: [EK-932] add settings tests

直接 commit:
  └─ fix: [EK-938] hotfix for crash
```

**生成的 Release Note：**
```
主要更新:
- [EK-927] adjust tooltip rendering timing
- [EK-930] fix logout animation
- [EK-932] add user settings page
- [EK-935] fix settings validation
- [EK-938] hotfix for crash
```

**說明：**
- PR #126: 1 個 issue → 1 條 release note
- PR #128: 1 個 issue（多個 commits） → 1 條 release note
- PR #130: 2 個不同 issues → 2 條 release notes
- 直接 commit: 1 條 release note

### 去重與整理規則

#### 基本原則
- 以 **branch merge** 為單位（一個 PR = 一條或多條 Release note）
- 如果一個 branch 內有多個不同的 `[EK-XXX]`，則按照不同的 issue 分別列出
- 相同的 `[EK-XXX]` 只顯示一次

#### 範例說明

**情況 1：一個 branch，一個 issue**
```
PR #126: fix-tooltip
  ├─ commit 1: fix: [EK-927] adjust tooltip rendering timing
  ├─ commit 2: fix: [EK-927] update tests
  └─ commit 3: fix: [EK-927] refine animation

→ Release Note:
- [EK-927] adjust tooltip rendering timing
```

**情況 2：一個 branch，多個不同 issues**
```
PR #130: feature-improvements
  ├─ commit 1: feat: [EK-930] add user settings page
  ├─ commit 2: fix: [EK-932] fix logout animation
  └─ commit 3: feat: [EK-930] add settings validation

→ Release Note:
- [EK-930] add user settings page
- [EK-932] fix logout animation
```

**情況 3：多個 branches**
```
PR #126: fix-tooltip
  └─ fix: [EK-927] adjust tooltip rendering timing

PR #128: fix-logout
  └─ fix: [EK-927] fix logout tooltip issue

→ Release Note:
- [EK-927] adjust tooltip rendering timing
- [EK-927] fix logout tooltip issue
（同一個 issue，但來自不同 PR，所以分別列出）
```

#### 過濾規則
- 過濾掉純 merge commits（如 `Merge branch 'dev'`）
- 過濾掉版本更新 commits（如 `chore: 更新 QA 版本`）
- 保留有實際功能描述的 commits

## 前置條件

### 必需工具
- ✅ Git（已配置好 remote）
- ✅ Gradle wrapper（`./gradlew`）
- ✅ Firebase App Distribution 配置
  - `firebase-service-account.json` 在專案根目錄
  - 已設定 Dev 和 QA 測試群組
- ✅ Jira MCP Server（`jira-extended`）
  - 用於驗證和修正 Jira issue 狀態
  - 需要 `jira_get_issue`、`jira_transition_issue`、`jira_update_assignee`、`jira_add_comment` 工具

### 必需檔案
- ✅ `gradle/libs.versions.toml`
- ✅ `app/build.gradle.kts`
- ✅ Firebase 配置檔案

### 權限要求
- ✅ 可以推送到 `origin/QA` branch
- ✅ Firebase App Distribution 發布權限

## 版本號規則詳解

### appVersionCode 格式說明
- 可變位數：主版本(可變) + 次版本(2) + 修訂版本(2) + 構建號(4)
- 主版本位數取決於 `appVersionName` 的第一個數字位數（如 1 為 1 位，10 為 2 位，100 為 3 位）
- 次版本和修訂版本固定為 2 位（單位數左側補 0）
- 構建號固定為 4 位
- 判斷版本是否改變：比較除構建號外的所有位數

### 規則 1: 版本號未變時（構建號遞增）
```
appVersionName = "1.2.3"
appVersionCode = "102030001"

版本部分 "10203" = 1(主) + 02(次) + 03(修訂) 與 "1.2.3" 相同
→ 新 appVersionCode = "102030002"（構建號 +1）
```

### 規則 2: 版本號已更新時（構建號重置）
```
appVersionName = "1.2.4"（從 "1.2.3" 更新）
appVersionCode = "102030010"

版本部分 "10203" ≠ "1.2.4"（應為 "10204"）
→ 新 appVersionCode = "102040001"（重置構建號為 0001）
```

### 規則 3: 次版本和修訂版本為多位數
```
appVersionName = "1.20.30"
appVersionCode = "120300001"

分解：1(主) + 20(次) + 30(修訂) + 0001(構建) [9 位數]
```

### 規則 4: 次版本和修訂版本單位數自動補零
```
appVersionName = "2.3.5"
appVersionCode = "203050001"

分解：2(主) + 03(次，補零) + 05(修訂，補零) + 0001(構建) [9 位數]
```

### 規則 5: 主版本為多位數
```
appVersionName = "10.2.3"
appVersionCode = "1002030001"

分解：10(主) + 02(次，補零) + 03(修訂，補零) + 0001(構建) [10 位數]
```

```
appVersionName = "15.20.8"
appVersionCode = "1520080001"

分解：15(主) + 20(次) + 08(修訂，補零) + 0001(構建) [10 位數]
```

```
appVersionName = "100.5.12"
appVersionCode = "100051200001"

分解：100(主) + 05(次，補零) + 12(修訂) + 0001(構建) [12 位數]
```

### 版本號對應關係
| appVersionName | 版本部分拆解 | appVersionCode 範例 | 總位數 |
|---------------|-----------|-------------------|-------|
| 1.2.3 | 1 + 02 + 03 | 102030001 | 9 |
| 1.2.10 | 1 + 02 + 10 | 102100001 | 9 |
| 1.20.3 | 1 + 20 + 03 | 120030001 | 9 |
| 2.0.0 | 2 + 00 + 00 | 200000001 | 9 |
| 10.2.3 | 10 + 02 + 03 | 1002030001 | 10 |
| 10.5.8 | 10 + 05 + 08 | 1005080001 | 10 |
| 15.20.8 | 15 + 20 + 08 | 1520080001 | 10 |
| 100.5.12 | 100 + 05 + 12 | 100051200001 | 12 |

## 故障排除

### 問題：Git merge 衝突
**解決方案：**
- 手動解決衝突後重新執行 `/qa-release`
- 或先執行 `git merge --abort` 後再試

### 問題：Firebase 上傳失敗
**檢查項目：**
1. `firebase-service-account.json` 是否存在
2. 網路連接是否正常
3. Firebase 專案權限是否正確

### 問題：Gradle build 失敗
**解決方案：**
- 檢查編譯錯誤並修復
- 確保 Android SDK 已正確安裝
- 執行 `./gradlew clean` 後重試

## 執行過程

```
📋 Step 1: 切換並合併分支
   ├─ git stash（如有未提交變更）
   ├─ git checkout dev
   ├─ git pull
   ├─ git checkout QA
   └─ git merge dev --no-edit

📋 Step 2: 自動生成 Release Notes
   ├─ git log QA..dev --oneline（查詢 dev 新增的 commits）
   ├─ 識別 PR/branch merges
   ├─ 按 PR 分組所有 commits
   ├─ 從每個 PR 中提取不同的 Jira issues（[EK-XXX] 或 EK-XXX）
   ├─ 提取功能描述（fix、feat、chore 等）
   ├─ 去重處理（每個 PR 內不同的 issue 分別列出）
   └─ 整理成 Release Note 列表

📋 Step 3: 版本號管理
   ├─ 讀取 gradle/libs.versions.toml
   ├─ 解析當前版本號
   ├─ 計算新版本號
   └─ 更新 appVersionCode

📋 Step 4: 更新 Release Notes
   └─ 修改 app/build.gradle.kts（使用步驟 2 生成的內容）

📋 Step 5: 提交並推送
   ├─ git add gradle/libs.versions.toml app/build.gradle.kts
   ├─ git commit -m "chore: 更新 QA 版本..."
   └─ git push origin QA

📋 Step 6: Firebase 部署
   ├─ ./gradlew createReleaseNotes
   ├─ ./gradlew assembleQaRelease
   └─ ./gradlew appDistributionUploadQaRelease

📋 Step 7: Jira Issue 驗證與修正
   ├─ 從 Release Notes 提取所有 Jira issue（EK-XXX）
   ├─ 從 git log 提取每個 issue 對應的 PR 號碼
   ├─ 逐一檢查每個 issue：
   │   ├─ jira_get_issue 取得 issue 詳情
   │   ├─ 檢查狀態是否為「QA 測試」→ 否則 jira_transition_issue
   │   ├─ 檢查受託人是否為回報人 → 否則 jira_update_assignee
   │   └─ 檢查最新留言是否包含版號和 PR 連結 → 否則 jira_add_comment
   └─ 輸出驗證結果摘要

✅ 完成！
```

## 注意事項

1. **自動推送：** 此 skill 會自動推送到遠端，請確認變更無誤
2. **版本遞增：** 版本號會自動計算，無需手動指定
3. **Release Note 自動生成：** 會從 dev branch 的 commit 歷史自動提取，建議 commit 訊息包含 Jira issue 編號和清晰的描述
4. **Commit 訊息格式：** 建議使用 `fix: [EK-XXX] 描述` 或 `feat: [EK-XXX] 描述` 格式，方便自動提取
5. **PR 組織建議：**
   - 一個 PR 專注於一個功能或修復
   - 如果 PR 內有多個相關但不同的 issues，系統會自動分別列出
   - 每個不同的 `[EK-XXX]` 會生成一條獨立的 release note
6. **Firebase 分發：** APK 會自動分發給 Dev 和 QA 群組的所有測試人員
7. **構建時間：** 完整流程約需 3-5 分鐘（視專案大小而定）

## 相關資源

- [Firebase App Distribution 文檔](https://firebase.google.com/docs/app-distribution)
- [Gradle 配置](../../app/build.gradle.kts)
- [版本管理](../../gradle/libs.versions.toml)
