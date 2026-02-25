# QA Release Skill - 詳細文檔

## 📖 目錄

- [概述](#概述)
- [安裝與配置](#安裝與配置)
- [使用指南](#使用指南)
- [版本號管理系統](#版本號管理系統)
- [工作流程詳解](#工作流程詳解)
- [故障排除](#故障排除)
- [最佳實踐](#最佳實踐)
- [FAQ](#faq)

## 概述

QA Release Skill 是一個完全自動化的 QA 版本發布工具，它將原本需要 10+ 個手動步驟的流程簡化為一個命令。

### 主要特性

- 🚀 **一鍵發布** - 單一命令完成所有步驟
- 🤖 **智能版本管理** - 自動計算和更新版本號
- 📝 **自動生成 Release Notes** - 從 dev branch commit 歷史自動提取更新內容
- 🏷️ **Jira 整合** - 自動識別並提取 Jira issue 編號
- ☁️ **雲端部署** - 自動上傳到 Firebase App Distribution
- 🔒 **安全可靠** - 包含完整的錯誤檢查和回滾機制

### 適用場景

✅ **適合使用：**
- 定期 QA 版本發布
- 緊急修復版本
- 功能測試版本
- Sprint 結束時的版本發布

❌ **不適合使用：**
- Production 版本發布（使用其他流程）
- 需要手動審查的重大變更
- 多個分支同時發布

## 安裝與配置

### 前置需求

#### 1. 軟體需求

```bash
# 檢查 Git
git --version
# 需要: Git 2.0+

# 檢查 Gradle
./gradlew --version
# 需要: Gradle 8.0+

# 檢查 Firebase CLI（可選）
firebase --version
```

#### 2. Firebase 配置

確保專案根目錄有：
```
ekkorn-android/
├── firebase-service-account.json  ← 必需
├── app/
│   └── google-services.json       ← 必需
└── ...
```

獲取 `firebase-service-account.json`：
1. 前往 [Firebase Console](https://console.firebase.google.com/)
2. 選擇專案 > 設定 > 服務帳戶
3. 生成新的私密金鑰
4. 下載並重命名為 `firebase-service-account.json`

#### 3. Git 權限

確認你有 QA branch 的推送權限：
```bash
git ls-remote --heads origin QA
```

#### 4. Firebase 測試群組

確認 Firebase Console 中已創建：
- `Dev` 測試群組
- `QA` 測試群組

### 驗證配置

執行以下命令驗證配置：

```bash
# 1. 檢查 Firebase 配置
ls firebase-service-account.json
ls app/google-services.json

# 2. 檢查版本檔案
cat gradle/libs.versions.toml | grep -E "appVersion(Name|Code)"

# 3. 檢查 build.gradle.kts
grep -A5 "createReleaseNotes" app/build.gradle.kts

# 4. 測試 Firebase 連接
./gradlew --dry-run appDistributionUploadQaRelease
```

如果所有檢查都通過，你可以開始使用了！

## 使用指南

### 基本使用

```bash
/qa-release
```

### 自動化流程

1. **啟動命令**
   ```
   你: /qa-release
   ```

2. **自動提取更新內容**
   系統會自動從 dev branch 的 commit 歷史中提取：
   - Jira issue 編號（如 [EK-927]）
   - Commit 描述和功能說明
   - PR 標題和內容

3. **自動執行**
   系統會自動執行所有步驟並顯示進度

4. **獲取結果**
   ```
   ✅ 完成！

   Release Notes:
   - [EK-927] 調整 tooltip 渲染時機
   - [EK-930] 修正登出頁面過渡動畫
   - [EK-932] 新增使用者設定頁面

   版本更新：
   - appVersionCode: 102000020 → 102000021
   - appVersionName: 1.2.0

   Firebase 連結：
   - Console: https://console.firebase.google.com/...
   - 下載: https://appdistribution.firebase.google.com/...
   ```

### Release Note 自動生成

系統會自動從以下來源提取更新內容：

#### Commit 訊息格式
推薦使用以下格式以獲得最佳的自動提取效果：

```bash
# 包含 Jira issue
fix: [EK-927] adjust tooltip rendering timing
feat: [EK-932] add user settings page

# 不包含 Jira issue
fix: 修正登出頁面過渡動畫
feat: 新增儀表板功能
```

#### 自動識別規則
- **Jira Issue**: `[EK-XXX]` 或 `EK-XXX` 格式
- **Commit 類型**: `fix:`、`feat:`、`chore:`、`refactor:` 等
- **PR 標題**: 從 merge commit 提取
- **去重**: 相同 issue 只顯示一次

## 版本號管理系統

### 版本號格式

```
appVersionCode = X(XX...)YYZZBBBB

X(XX...) = 主版本號（可變位數，如 1、10、100）
YY       = 次版本號（2 位數，左側補零）
ZZ       = 修訂版本號（2 位數，左側補零）
BBBB     = 構建號（4 位數，左側補零）
```

### 示例

| appVersionName | 版本部分拆解 | 完整 appVersionCode | 總位數 |
|---------------|-----------|-------------------|-------|
| 1.0.0         | 1 + 00 + 00 | 100000001 | 9 |
| 1.2.3         | 1 + 02 + 03 | 102030001 | 9 |
| 1.20.15       | 1 + 20 + 15 | 120150001 | 9 |
| 10.2.3        | 10 + 02 + 03 | 1002030001 | 10 |
| 15.20.8       | 15 + 20 + 08 | 1520080001 | 10 |
| 100.5.12      | 100 + 05 + 12 | 100051200001 | 12 |

### 自動更新規則

#### 規則 1: 構建號遞增

**條件：** `appVersionCode` 版本部分 == `appVersionName` 對應數字

```
當前狀態：
appVersionName = "1.2.3"
appVersionCode = "102030001"

版本部分: 10203 = 1(主) + 02(次) + 03(修訂) ✅ 匹配

更新後：
appVersionCode = "102030002"  （構建號 +1）
```

#### 規則 2: 構建號重置

**條件：** `appVersionCode` 版本部分 != `appVersionName` 對應數字

```
當前狀態：
appVersionName = "1.2.4"  （版本號已在其他地方更新）
appVersionCode = "102030010"

版本部分: 10203 ≠ 10204 ❌ 不匹配

更新後：
appVersionCode = "102040001"  （重置構建號為 0001）
```

#### 規則 3: 主版本多位數

**條件：** 主版本號 >= 10

```
當前狀態：
appVersionName = "10.2.3"
appVersionCode = "1002030001"

版本部分: 100203 = 10(主) + 02(次) + 03(修訂) ✅ 匹配

更新後：
appVersionCode = "1002030002"  （構建號 +1）
```

### 手動調整版本號

如果需要發布新的主版本、次版本或修訂版本：

1. **先更新 appVersionName**
   ```toml
   # gradle/libs.versions.toml
   appVersionName = "1.2.4"  # 從 1.2.3 更新
   ```

2. **執行 `/qa-release`**
   系統會自動將 `appVersionCode` 從 `102030010` 更新為 `102040001`

**範例（主版本升級）：**
```toml
# 從 1.2.3 升級到 2.0.0
appVersionName = "2.0.0"

# 系統會自動更新：
# appVersionCode: 102030010 → 200000001
```

**範例（主版本超過 10）：**
```toml
# 從 9.5.8 升級到 10.0.0
appVersionName = "10.0.0"

# 系統會自動更新：
# appVersionCode: 905080005 → 1000000001（增加到 10 位數）
```

## 工作流程詳解

### 完整流程圖

```
開始
  │
  ├─► [1] 準備環境
  │     ├─► Stash 當前變更（如有）
  │     ├─► Checkout QA branch
  │     └─► Merge dev → QA
  │
  ├─► [2] 自動生成 Release Notes
  │     ├─► git log QA..dev（查詢新 commits）
  │     ├─► 提取 Jira issue 編號
  │     ├─► 提取功能描述
  │     └─► 整理成列表
  │
  ├─► [3] 版本號管理
  │     ├─► 讀取 libs.versions.toml
  │     ├─► 解析版本號
  │     ├─► 計算新版本號
  │     └─► 更新 appVersionCode
  │
  ├─► [4] 更新 Release Notes
  │     └─► 更新 build.gradle.kts（使用步驟 2 內容）
  │
  ├─► [5] Git 操作
  │     ├─► git add
  │     ├─► git commit
  │     └─► git push origin QA
  │
  ├─► [6] Firebase 部署
  │     ├─► createReleaseNotes
  │     ├─► assembleQaRelease
  │     └─► appDistributionUploadQaRelease
  │
  └─► [7] Jira Issue 驗證與修正
        ├─► 從 Release Notes 提取 Jira issues
        ├─► 從 git log 提取對應的 PR 號碼
        ├─► 逐一檢查每個 issue：
        │     ├─► 狀態是否為「QA 測試」
        │     ├─► 受託人是否為回報人
        │     └─► 最新留言是否包含版號和 PR 連結
        ├─► 自動修正不符合的項目
        └─► 輸出驗證結果摘要
              │
              └─► 完成！
```

### 各步驟詳解

#### Step 1: 準備環境

**操作：**
```bash
# 2.1 Stash 未提交變更
git stash

# 2.2 切換到 QA
git checkout QA

# 2.3 合併 dev
git merge dev --no-edit
```

**錯誤處理：**
- 如果合併衝突 → 顯示錯誤，要求手動解決
- 如果 QA branch 不存在 → 創建並推送

#### Step 2: 自動生成 Release Notes

**目的：** 從 dev branch 的 commit 歷史自動提取更新內容

**查詢命令：**
```bash
# 查詢 QA 到 dev 之間的所有新 commits
git log QA..dev --oneline
```

**提取邏輯：**

1. **識別 PR/Branch Merge**
   - 從 merge commits 識別每個 PR
   - 範例：`Merge pull request #126` → PR #126

2. **按 PR 分組 Commits**
   - 將 PR 內的所有 commits 分組
   - 提取每個 PR 內的所有不同 Jira issues

3. **Jira Issue 提取與去重**
   - 正則表達式：`\[?(EK-\d+)\]?`
   - 範例：`fix: [EK-927] adjust timing` → `[EK-927]`
   - **去重規則：**
     - 一個 PR = 一條或多條 release note
     - 如果 PR 內有多個不同的 `[EK-XXX]`，分別列出
     - 每個不同的 `[EK-XXX]` 只取第一個有意義的描述

4. **Commit 類型識別**
   - `fix:` → 修復
   - `feat:` → 新功能
   - `chore:` → 維護
   - `refactor:` → 重構

**範例說明：**
```
PR #126（1 個 issue）：
  └─ [EK-927] adjust tooltip timing
→ 1 條 release note

PR #130（2 個不同 issues）：
  ├─ [EK-930] add settings page
  └─ [EK-932] fix validation
→ 2 條 release notes
```

**輸出格式：**
```
主要更新:
- [EK-927] adjust tooltip rendering timing
- [EK-930] add user settings page
- [EK-932] fix settings validation
```

#### Step 3: 版本號管理

**讀取版本：**
```bash
# 從 gradle/libs.versions.toml 讀取
appVersionCode = "102030001"
appVersionName = "1.2.3"
```

**計算邏輯：**
```python
def calculate_new_version(version_name, version_code):
    # 解析 version_name "1.2.3" → [1, 2, 3]
    parts = version_name.split('.')
    major = int(parts[0])
    minor = int(parts[1])
    patch = int(parts[2])

    # 計算預期版本部分
    # major 可為多位數，minor 和 patch 固定 2 位
    expected_version = f"{major}{minor:02d}{patch:02d}"  # "10203"

    # 取得當前版本部分（除去後 4 位構建號）
    current_version = version_code[:-4]  # "10203"

    if current_version == expected_version:
        # 規則 1: 遞增構建號
        return str(int(version_code) + 1)  # "102030002"
    else:
        # 規則 2: 重置構建號
        return f"{expected_version}0001"  # "102040001"
```

**更新檔案：**
```toml
# gradle/libs.versions.toml
appVersionCode = "102030002"  # 更新這一行
```

#### Step 4: 更新 Release Notes

**更新位置：**
```kotlin
// app/build.gradle.kts
val releaseNotes = """
Release Build
建置時間: $timestamp
Git Commit: ${gitHash.toString().trim()}
Android 版本: $versionName ($versionCode)

主要更新:
- [EK-927] 調整 tooltip 渲染時機  ← 自動生成的內容
- [EK-930] 修正登出頁面過渡動畫
- [EK-932] 新增使用者設定頁面
""".trimIndent()
```

**替換邏輯：**
```kotlin
old_string = """
主要更新:
- [EK-920] 舊的更新內容
"""

new_string = """
主要更新:
- [EK-927] 調整 tooltip 渲染時機
- [EK-930] 修正登出頁面過渡動畫
- [EK-932] 新增使用者設定頁面
"""
```

#### Step 5: Git 操作

**Commit 訊息格式：**
```
chore: 更新 QA 版本至 {version_name} ({version_code})

- 更新 appVersionCode: {old_code} -> {new_code}
- 更新 release notes:
  - [EK-927] 調整 tooltip 渲染時機
  - [EK-930] 修正登出頁面過渡動畫
  - [EK-932] 新增使用者設定頁面

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**執行命令：**
```bash
git add gradle/libs.versions.toml app/build.gradle.kts
git commit -m "..."
git push origin QA
```

#### Step 6: Firebase 部署

**Gradle 任務：**
```bash
./gradlew uploadQaRelease
```

**內部步驟：**
1. `createReleaseNotes` - 生成 release-notes.txt
2. `assembleQaRelease` - 建置 APK
3. `appDistributionUploadQaRelease` - 上傳到 Firebase

**上傳配置：**
```kotlin
// app/build.gradle.kts
firebaseAppDistribution {
    artifactType = "APK"
    releaseNotesFile = "app/src/main/assets/release-notes.txt"
    groups = "Dev,QA"  // 分發給這些群組
    serviceCredentialsFile = "${rootProject.projectDir}/firebase-service-account.json"
}
```

#### Step 7: Jira Issue 驗證與修正

**目的：** 確保此版本涉及的所有 Jira issue 狀態正確，受託人正確，留言包含版號和 PR 連結。

**執行流程：**

1. **提取 Jira Issues 和 PR 對應關係**
   - 從步驟 2 生成的 Release Notes 中提取所有 `[EK-XXX]` issue
   - 從 `git log QA..dev` 的 merge commit 中提取每個 issue 對應的 PR 號碼
   - PR URL 格式：`https://github.com/SHOW-YOU-APP/ekkorn-android/pull/{PR_NUMBER}`

2. **逐一驗證每個 Issue**

```javascript
// 對每個 Jira issue 執行以下檢查：

// 2.1 取得 issue 詳情
mcp__jira-extended__jira_get_issue({
  issueKey: "EK-927",
  includeComments: true
})
// 回傳：status, reporter, assignee, comments

// 2.2 檢查狀態
// 如果 status.name !== "QA 測試"：
mcp__jira-extended__jira_transition_issue({
  issueKey: "EK-927",
  transitionName: "QA 測試"
})

// 2.3 檢查受託人
// 如果 assignee.accountId !== reporter.accountId：
mcp__jira-extended__jira_update_assignee({
  issueKey: "EK-927",
  accountId: "{reporter.accountId}"
})

// 2.4 檢查最新留言
// 如果最新留言不包含新的 appVersionCode 和 PR 連結：
mcp__jira-extended__jira_add_comment({
  issueKey: "EK-927",
  comment: "QA 版本已發布，版號：102030002，相關 PR：[PR #126|https://github.com/SHOW-YOU-APP/ekkorn-android/pull/126]"
})
```

3. **輸出驗證結果**
```
📋 Jira Issue 驗證結果：
- [EK-927] ✅ 狀態: QA 測試 | ✅ 受託人: 回報人 | ✅ 留言: 已包含版號和 PR 連結
- [EK-930] ⚠️ 狀態: 已修正→QA 測試 | ✅ 受託人: 回報人 | ⚠️ 留言: 已補充版號和 PR 連結
- [EK-932] ✅ 狀態: QA 測試 | ⚠️ 受託人: 已修正→回報人 | ✅ 留言: 已包含版號和 PR 連結
```

**錯誤處理：**
- 如果 issue 不存在或無法存取 → 跳過並在結果中標記 ❌
- 如果無法取得可用的 transition → 跳過狀態修改並在結果中標記 ❌
- 如果無法找到對應的 PR → 留言中省略 PR 連結，只包含版號

## 故障排除

### 常見錯誤

#### 錯誤 1: Git merge 衝突

**錯誤訊息：**
```
error: Your local changes to the following files would be overwritten by merge:
  app/build.gradle.kts
```

**解決方案：**
```bash
# 選項 A: Stash 變更
git stash
/qa-release

# 選項 B: Commit 變更
git add .
git commit -m "WIP"
/qa-release
```

#### 錯誤 2: Firebase 上傳失敗

**錯誤訊息：**
```
Error: Could not find service account file
```

**檢查清單：**
```bash
# 1. 檢查檔案是否存在
ls firebase-service-account.json

# 2. 檢查檔案權限
chmod 600 firebase-service-account.json

# 3. 驗證 JSON 格式
cat firebase-service-account.json | python -m json.tool

# 4. 檢查 Firebase 專案 ID
grep project_id firebase-service-account.json
```

#### 錯誤 3: 版本號計算錯誤

**問題：** 版本號更新不符合預期

**檢查：**
```bash
# 1. 查看當前版本
cat gradle/libs.versions.toml | grep appVersion

# 2. 手動計算
# appVersionName = "1.2.3" → 版本部分應為 "10203"
# appVersionCode = "102030001" → 版本部分是 "10203" ✅

# 3. 範例（主版本 >= 10）
# appVersionName = "10.2.3" → 版本部分應為 "100203"
# appVersionCode = "1002030001" → 版本部分是 "100203" ✅

# 4. 如果不匹配，手動修正
# 編輯 gradle/libs.versions.toml
```

#### 錯誤 4: Gradle build 失敗

**錯誤訊息：**
```
Execution failed for task ':app:compileQaReleaseKotlin'
```

**解決方案：**
```bash
# 1. Clean build
./gradlew clean

# 2. 檢查編譯錯誤
./gradlew assembleQaRelease --stacktrace

# 3. 修復錯誤後重新執行
/qa-release
```

### Debug 模式

查看詳細日誌：

```bash
# 手動執行各步驟以查看詳細輸出

# Step 1-2: 合併分支
git checkout QA
git merge dev -v

# Step 3-4: 檢查版本更新
git diff gradle/libs.versions.toml
git diff app/build.gradle.kts

# Step 5: 檢查 commit
git log -1 --stat

# Step 6: 詳細建置日誌
./gradlew uploadQaRelease --info --stacktrace
```

## 最佳實踐

### 發布前檢查

✅ **推薦流程：**

```bash
# 1. 確保 dev branch 是最新的
git checkout dev
git pull origin dev

# 2. 在本地測試
./gradlew assembleDevDebug
# 測試 app...

# 3. 執行 QA release
/qa-release
```

### 版本號管理

✅ **推薦：**
- 讓 skill 自動管理 `appVersionCode`
- 只手動更新 `appVersionName`（新功能發布時）
- 遵循語義化版本規範

❌ **避免：**
- 手動修改 `appVersionCode`
- 跳過版本號
- 使用非標準格式

### Commit 訊息撰寫（影響自動生成的 Release Notes）

✅ **好的範例：**

**情況 1：一個 PR，一個 Issue**
```bash
# PR #126: fix-tooltip
git commit -m "fix: [EK-927] 修復登入頁面閃退問題"
git commit -m "fix: [EK-927] 新增錯誤處理"
git commit -m "test: [EK-927] 新增單元測試"

# → Release Note: [EK-927] 修復登入頁面閃退問題
```

**情況 2：一個 PR，多個 Issues**
```bash
# PR #130: feature-improvements
git commit -m "feat: [EK-930] 新增個人資料編輯功能"
git commit -m "fix: [EK-932] 修正驗證邏輯"
git commit -m "feat: [EK-930] 新增欄位驗證"

# → Release Notes:
#   - [EK-930] 新增個人資料編輯功能
#   - [EK-932] 修正驗證邏輯
```

❌ **不好的範例：**
```bash
fix bug
update
調整
WIP
Merge branch 'dev'
```

**撰寫指南：**
- 使用 Conventional Commits 格式：`type: [ISSUE] description`
- 包含 Jira issue 編號（如果有）
- 描述要清晰具體，避免過於籠統
- 使用中文或英文均可，但要保持一致性
- **一個 PR 專注於一個功能，但可以包含多個相關的 issues**
- 第一個 commit 的描述會被用作 release note 的內容

### 測試群組管理

建議配置：
- **Dev 群組**: 開發團隊（5-10 人）
- **QA 群組**: QA 團隊 + PM（10-20 人）

## FAQ

### Q1: 可以跳過某些步驟嗎？

A: 不建議。整個流程是設計成原子操作的。如果需要客製化，請手動執行各步驟。

### Q2: 如何回滾發布？

A:
```bash
# 1. 回滾 git commit
git checkout QA
git reset --hard HEAD~1
git push -f origin QA

# 2. Firebase 上無法刪除已發布版本，但可以：
# - 在 Console 中停用該版本
# - 發布新版本覆蓋
```

### Q3: 支援其他分支嗎？

A: 當前版本固定為 `dev → QA`。如需其他分支，需要修改 SKILL.md。

### Q4: 建置時間可以優化嗎？

A:
```bash
# 啟用 Gradle daemon（預設已啟用）
./gradlew --daemon

# 增加 heap size
# 編輯 gradle.properties
org.gradle.jvmargs=-Xmx4096m
```

### Q5: 可以同時發布多個版本嗎？

A: 不建議。建議依序發布，確保每個版本都經過測試。

## 相關資源

- [SKILL.md](./SKILL.md) - Skill 技術文檔
- [QUICKSTART.md](./QUICKSTART.md) - 快速開始指南
- [Firebase App Distribution 文檔](https://firebase.google.com/docs/app-distribution)
- [Android Gradle Plugin 文檔](https://developer.android.com/build)
- [語義化版本規範](https://semver.org/lang/zh-TW/)

## 更新日誌

### v1.0.0 (2026-01-20)
- ✨ 初始版本
- ✅ 自動合併分支
- ✅ 智能版本號管理
- ✅ Release notes 自動更新
- ✅ Firebase 自動部署

---

**立即開始使用：**
```bash
/qa-release
```
