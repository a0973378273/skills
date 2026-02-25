---
name: scheduled-task
description: 自動排程執行 Jira 任務的 skill。在指定時間窗口（21:00-07:00）內自動執行，檢查 usage < 80%，自動處理 git stash/commit，並為每個 issue 創建獨立 branch。適合批次處理多個 Jira issues。
---

# 排程任務執行器 (Scheduled Task Executor)

自動排程執行 Jira 任務或開發工作的 skill。在指定時間窗口內自動執行任務，並智能管理 git 工作流程。

## 快速使用

使用 Jira Issue：
```bash
/scheduled-task EK-995
```

使用完整 URL：
```bash
/scheduled-task https://showyouapp.atlassian.net/browse/EK-978
```

批次處理多個任務：
```bash
/scheduled-task EK-995 EK-978 EK-980
```

## 執行流程

當你執行這個 skill 時，系統會自動完成以下步驟：

### 階段 1: 任務分析與規劃

1. **📋 獲取並分析 Jira Issue(s)**
   - 解析 Jira URL 或 Issue Key
   - 獲取 issue 詳細資訊（summary, description, priority）
   - 分析需求並拆解成 TODO 清單
   - 建立任務間的依賴關係

2. **💬 創建排程**
   - 顯示所有待執行任務
   - 說明執行條件和時間窗口
   - **直接進入排程，不詢問用戶確認**

### 階段 2: 等待執行時間

3. **⏰ 時間窗口控制**
   - **執行時間**: 只在晚上 21:00 - 早上 07:00 執行
   - 不在時間窗口時：顯示需等待時間並暫停
   - 到達執行時間後：自動繼續執行

### 階段 3: 執行循環（每個 Issue）

對於每個 Jira Issue，依序執行以下步驟：

4. **📊 檢查執行條件並準備環境**
   ```
   ⏰ 檢查時間（21:00-07:00）
      ├─ 不在範圍 → 等待到 21:00
      └─ 在範圍 → 繼續

   📊 檢查 Usage < 80%
      ├─ 超過 80% → 暫停並通知
      └─ 未超過 → 繼續

   🔍 檢查 Git 狀態
      ├─ 不乾淨 → 自動 stash
      └─ 乾淨 → 繼續

   🌿 切換到最新的 dev branch
      ├─ git checkout dev
      ├─ git pull origin dev
      └─ 確保從最新的 dev 創建 branch
   ```

5. **▶️ 執行 Issue 的所有任務**
   - 依 TODO 清單順序執行
   - 更新任務狀態（pending → in_progress → completed）
   - **遇到問題時自動嘗試解決**：
     - 分析錯誤原因
     - 嘗試替代方案
     - 查找相關文件或資源
     - 調整實作策略
     - 只有在所有方法都嘗試後才報告問題
   - **目標：不停止，持續推進直到完成**

6. **🌿 Git 工作流程**
   ```
   創建 feature branch（從最新的 dev）
      ↓
   實作所有程式碼變更
      ↓
   Stage 變更的檔案
      ↓
   Commit 變更（規範格式）
      ↓
   顯示完成資訊
   ```

   **注意**: Branch 已在步驟 4 創建，確保從最新的 dev 出來

7. **⤴️ 進入下一個 Issue**
   - 重複步驟 4-6
   - 直到所有 Issues 完成

### 階段 4: 完成總結

8. **📊 顯示執行摘要**
   - 已完成的 Issues
   - 創建的 branches
   - 提交的 commits
   - 總執行時間
   - Token usage 統計

9. **💡 提供後續建議**
   - 推送 branches
   - 創建 Pull Requests
   - 恢復 stashed 變更

## 核心功能

### 1. ⏰ 時間窗口控制

**執行時間**: 21:00 - 07:00（晚上 9 點到早上 7 點）

```
當前時間 02:00 → ✅ 在執行窗口內，立即執行
當前時間 15:00 → ❌ 不在窗口內，等待 6 小時到 21:00
當前時間 08:00 → ❌ 不在窗口內，等待 13 小時到 21:00
```

**自定義時間**:
```bash
/scheduled-task EK-995 --start-time=22:00 --end-time=06:00
```

**立即執行（測試用）**:
```bash
/scheduled-task EK-995 --now
```

### 2. 📊 Usage 監控

**檢查時機**: 每個 Issue 執行前

**計算方式**:
```
current_usage = (已使用 tokens / 總限制) × 100%

if current_usage >= 80%:
    if 在執行時間內 (21:00-07:00):
        暫停 1 小時後重新檢查
        重複直到 usage < 80% 或超出執行時間
    else:
        中止執行
else:
    繼續執行
```

**Usage 策略（自動重試）**:
| Usage | 時間窗口內 | 動作 |
|-------|-----------|------|
| < 80% | - | ✅ 正常執行 |
| >= 80% | 在窗口內 (21:00-07:00) | ⏸️ 暫停 1 小時，自動重試 |
| >= 80% | 超出窗口 | 🛑 中止執行 |

**自動重試流程**:
```
檢測到 usage >= 80%
   ↓
檢查是否在執行時間內？
   ├─ 是 → 暫停 1 小時
   │        ↓
   │      重新檢查 usage
   │        ├─ < 80% → 繼續執行
   │        └─ >= 80% → 再暫停 1 小時
   │
   └─ 否 → 中止執行並通知用戶
```

**自定義閾值**:
```bash
/scheduled-task EK-995 --max-usage=70
```

### 3. 🔄 Git 工作流程管理

#### 執行前準備

```bash
# 檢查 git 狀態
git status --porcelain

# 如果有未提交變更
→ 自動執行 stash
→ 記錄 stash 訊息
→ 繼續執行任務
```

**Stash 訊息格式**:
```
Auto stash before scheduled-task at 2026-02-04_21-00-00
```

#### 執行流程（每個 Issue）

**在執行任務前（步驟 4）：**

1. **處理 Git 狀態**
   ```bash
   # 如果有未提交變更，自動 stash
   git stash push -m "Auto stash before EK-995 at 2026-02-04_21-00-00"
   ```

2. **切換到最新的 dev branch**
   ```bash
   git checkout dev
   git pull origin dev
   ```

3. **創建 feature branch**
   ```bash
   # 格式: feat/{ISSUE-KEY}-{short-summary}
   git checkout -b feat/EK-995-fix-newcomer-bonus-timing
   ```

**執行任務（步驟 5）：**

4. **在新 branch 上實作所有變更**
   - 執行所有 TODO 任務
   - 修改程式碼
   - 完成所有實作

**完成後提交（步驟 6）：**

5. **Stage 相關變更**
   ```bash
   # 只 add 該 Issue 修改的檔案
   git add app/src/.../LoginViewModel.kt
   git add app/src/.../SomeOtherFile.kt
   ```

6. **Commit 變更**
   ```bash
   git commit -m "[EK-995] 修正新人獎勵時間驗證邏輯

   - 詳細變更說明
   - 變更點 1
   - 變更點 2

   Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
   ```

7. **記錄完成資訊**
   - Branch 名稱: `feat/EK-995-fix-newcomer-bonus-timing`
   - Commit hash
   - 修改的檔案列表

#### Branch 命名規則

```
feat/{ISSUE-KEY}-{short-summary}
```

**範例**:
- `feat/EK-995-fix-newcomer-bonus-timing`
- `feat/EK-978-fix-guest-task-navigation`
- `feat/EK-920-add-dark-mode-toggle`

#### Commit 訊息格式

```
[{ISSUE-KEY}] {一行摘要}

{詳細描述}
- 變更點 1
- 變更點 2

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

### 4. 🎯 自動執行循環

每一輪執行都會重新檢查所有條件並準備環境：

```
對於每個 Issue:
   ↓
⏰ 檢查時間 (21:00-07:00)
   ↓
📊 檢查 Usage < 80%
   ↓
🔍 檢查 Git 狀態
   ├─ 有未提交變更 → 自動 stash
   └─ 工作區乾淨 → 繼續
   ↓
🌿 準備 Git 環境
   ├─ git checkout dev
   ├─ git pull origin dev
   └─ git checkout -b feat/EK-XXX-...
   ↓
▶️ 執行該 Issue 的所有任務（在新 branch 上）
   ├─ 遇到問題自動嘗試解決
   ├─ 使用替代方案持續推進
   └─ 完成所有實作
   ↓
💾 Commit 變更
   ├─ git add [修改的檔案]
   └─ git commit -m "[EK-XXX] ..."
   ↓
⤴️ 返回檢查下一個 Issue
```

### 5. 🛡️ 安全機制

1. **時間保護**: 只在非工作時間執行，避免干擾
2. **Usage 保護**: 防止超出 token 限制
3. **Git 保護**:
   - 自動 stash 未提交變更
   - 在 stash 後切換到最新的 dev branch
   - 從最新的 dev 創建 feature branch
   - 確保不會丟失程式碼
4. **智能錯誤處理**:
   - 遇到問題自動嘗試解決
   - 使用多種策略持續推進
   - 只記錄無法解決的問題
   - 不輕易停止執行
5. **自動進入排程**: 任務拆解完成後直接進入排程，不詢問確認

## 使用範例

### 範例 1: 單一 Issue

```bash
/scheduled-task EK-995
```

**執行流程**:
```
15:30 - 分析 EK-995 並創建排程
        💬 「將在今晚 21:00 開始執行」

21:00 - ✅ 檢查條件並準備環境
        ⏰ 時間檢查通過
        📊 Usage: 62% (通過)
        💾 Stash 未提交變更
        🌿 切換到 dev: git checkout dev && git pull
        🌿 創建 branch: git checkout -b feat/EK-995-xxx

21:05 - ▶️ 執行 4 個 TODO（在新 branch 上）
        ├─ Task #1: 分析現有程式碼
        ├─ Task #2: 修改 ViewModel
        ├─ Task #3: 更新 UI
        └─ Task #4: 測試功能

21:25 - 💾 Commit 變更
        ✅ 完成！

21:30 - 💬 顯示摘要
        📦 Branch: feat/EK-995-xxx
        💾 Commit: a1b2c3d
```

### 範例 2: 批次處理多個 Issues

```bash
/scheduled-task EK-995 EK-978
```

**執行流程**:
```
15:00 - 分析兩個 issues，創建 8 個 TODO
        EK-978 依賴 EK-995
        💬 「將在今晚 21:00 開始執行」

21:00 - 【第一輪：EK-995】
        ✅ 檢查條件（時間、Usage、Git）
        💾 Stash 未提交變更
        🌿 切換到 dev 並更新
        🌿 創建 feat/EK-995-xxx branch
        ▶️ 執行 4 個 TODO（在新 branch 上）
        💾 Commit 變更

22:00 - 【第二輪：EK-978】
        ✅ 再次檢查所有條件
        🌿 切換回 dev 並更新
        🌿 創建 feat/EK-978-xxx branch
        ▶️ 執行 4 個 TODO（在新 branch 上）
        💾 Commit 變更

23:00 - ✅ 全部完成！
        💬 已創建 2 個獨立 branches
        📦 feat/EK-995-xxx
        📦 feat/EK-978-xxx
```

### 範例 3: 自定義選項

```bash
# 立即執行（跳過時間檢查）
/scheduled-task EK-995 --now

# 自定義時間窗口
/scheduled-task EK-995 --start-time=22:00 --end-time=06:00

# 調整 usage 閾值
/scheduled-task EK-995 --max-usage=70

# 禁止自動 stash
/scheduled-task EK-995 --no-stash

# 完成後自動推送
/scheduled-task EK-995 --auto-push

# 自動創建 PR
/scheduled-task EK-995 --auto-pr
```

## 參數說明

| 參數 | 類型 | 說明 | 範例 |
|-----|------|------|------|
| issue_keys | String[] | Jira issue 的 Key 或 URL（可多個） | `EK-995 EK-978` |
| --now | Flag | 立即執行（跳過時間檢查） | |
| --start-time | String | 自定義開始時間 | `--start-time=22:00` |
| --end-time | String | 自定義結束時間 | `--end-time=06:00` |
| --max-usage | Number | 自定義 usage 閾值（百分比） | `--max-usage=70` |
| --no-stash | Flag | 禁止自動 stash | |
| --no-commit | Flag | 不自動 commit | |
| --auto-push | Flag | 完成後自動推送到 remote | |
| --auto-pr | Flag | 完成後自動創建 PR | |
| --base-branch | String | 指定基礎 branch | `--base-branch=main` |

## 錯誤處理

### 時間窗口外執行

```
⏸️ 當前時間不在執行窗口內（21:00-07:00）

現在時間: 15:30
下次執行: 今晚 21:00
需等待: 5 小時 30 分鐘

選項:
- [等待] 等待到執行時間（預設）
- [立即執行] 使用 --now 立即執行
- [取消] 取消排程
```

### Usage 超過限制（自動處理）

**在執行時間內（21:00-07:00）**:
```
⚠️ Token Usage 已達 85%

已使用: 170,000
總限制: 200,000
剩餘: 30,000

⏸️ 自動暫停執行，等待 usage 降低...

當前時間: 22:30
執行窗口: 至 07:00 (還有 8.5 小時)

動作:
- 暫停 1 小時
- 23:30 時自動重新檢查 usage
- 如果 usage < 80%，自動繼續執行
- 如果仍 >= 80%，繼續等待 1 小時

💡 無需手動介入，系統會自動管理
```

**超出執行時間**:
```
⚠️ Token Usage 已達 85%

已使用: 170,000
總限制: 200,000
剩餘: 30,000

當前時間: 08:00 (超出執行窗口)

🛑 已中止執行

已完成: 1/3 Issues
未完成: 2 Issues

建議:
- 今晚 21:00 繼續執行剩餘任務
- 或等待 usage 降低後手動執行
```

### Git 工作區不乾淨

```
📝 檢測到未提交的變更:
   M  app/src/.../MainActivity.kt
   M  README.md

需要先處理這些變更才能執行任務。

選項:
- [Stash] 自動 stash（推薦）
- [手動處理] 手動處理後繼續
- [取消] 取消執行
```

### 任務執行遇到問題

**預設行為：自動嘗試解決，不停止執行**

```
⚠️ 遇到問題: #3 修改登入邏輯

問題: 找不到 LoginViewModel.kt

🔍 自動嘗試解決：
✓ 1. 搜索整個專案中的 LoginViewModel
     → 找到: app/src/main/java/.../login/LoginViewModel.kt

✓ 2. 更新路徑並繼續執行
     → 成功修改文件

✅ 問題已自動解決，繼續執行

─────────────────────────────────────────

⚠️ 遇到複雜問題: #5 整合新的 API

問題: API 規格與預期不符

🔍 自動嘗試解決：
✓ 1. 讀取 API 文檔
✓ 2. 分析實際的 response 格式
✓ 3. 調整 data model 以符合實際格式
✓ 4. 更新 repository 層的轉換邏輯

✅ 已採用替代方案，繼續執行

─────────────────────────────────────────

只有在嘗試所有方法後仍無法解決時，才會報告：

❌ 無法自動解決: #7 添加支付功能

問題: 需要支付 SDK 的 API key，無法從現有資源中找到

已嘗試:
✓ 搜索專案配置文件
✓ 檢查環境變數
✓ 查找相關文檔
✗ 無法找到必要的 credentials

💬 記錄問題並繼續下一個任務
   （在摘要中報告需要人工處理的項目）
```

**自動解決策略：**
1. 🔍 **搜索替代路徑** - 文件找不到時搜索整個專案
2. 🔄 **調整實作方式** - 遇到限制時使用替代方案
3. 📚 **查找參考** - 從現有程式碼中學習相似實作
4. 🛠️ **簡化需求** - 複雜功能先實作核心部分
5. 📝 **記錄問題** - 無法解決時記錄並繼續其他任務

## 進度追蹤

執行過程中會顯示即時進度：

```
┌────────────────────────────────────────────────┐
│ 🌙 排程任務執行中                              │
├────────────────────────────────────────────────┤
│ 開始時間: 2026-02-04 21:00:00                  │
│ 當前時間: 2026-02-04 22:15:32                  │
│ 執行時長: 1 小時 15 分鐘                       │
├────────────────────────────────────────────────┤
│ 總進度: ████████████░░░░ 50% (1/2 Issues)     │
├────────────────────────────────────────────────┤
│ ✅ EK-995 (已完成)                             │
│    ✅ #1-4 所有任務完成                        │
│    📦 Branch: feat/EK-995-...                  │
│    💾 Commit: a1b2c3d                          │
│                                                │
│ ⏳ EK-978 (執行中)                             │
│    ✅ #5 已完成                                │
│    ▶️  #6 進行中                               │
│    ⏸️ #7-8 等待中                              │
├────────────────────────────────────────────────┤
│ Token Usage: 125,430 / 200,000 (62.72%) ✅    │
│ 時間檢查: ✅ 在執行窗口內                       │
└────────────────────────────────────────────────┘
```

## 最佳實踐

### ✅ 執行前準備

1. **確保 Jira issue 描述清晰**
2. **準備好相關資源**（設計圖、API 文檔等）
3. **了解任務預估時間**（確保能在一個夜晚完成）
4. **檢查 git 倉庫狀態**

### ✅ 排程建議

1. **批次處理相關 issues**
   ```bash
   # 好：相關的功能一起處理
   /scheduled-task EK-995 EK-996 EK-997
   ```

2. **合理估計時間**
   - 簡單 bug fix: ~30 分鐘
   - 中等功能: 1-2 小時
   - 複雜功能: 2-4 小時

3. **避免過度排程**
   - 一次不超過 3-4 個中等任務
   - 或 1-2 個複雜任務

### ✅ 執行後檢查

1. **隔天早上檢查執行結果**
2. **Review 生成的程式碼變更**
3. **測試功能是否正常**
4. **創建 PR 並進行 code review**

## 與其他 Skills 整合

### 完整工作流程

```bash
# 1. 夜間自動執行
/scheduled-task EK-995 EK-978

# 2. 早上檢查結果，創建 PR
/jira-pr EK-995
/jira-pr EK-978

# 3. 發布到 QA
/qa-release
```

### 獨立使用

```bash
# 僅分析需求，不執行（在 jira-task 中處理）
/jira-task EK-995
> 「先不要執行，只列出 TODO」

# 使用 scheduled-task 排程執行
/scheduled-task --use-existing-tasks
```

## 故障排除

### Q: 任務一直在等待執行時間

**檢查**:
```bash
date  # 查看當前時間
```

**解決**:
- 確認當前時間是否在 21:00-07:00 之外
- 使用 `--now` 立即執行（測試用）

### Q: 無法識別 scheduled-task skill

**原因**: Claude Code 未重新掃描 skills

**解決**:
1. 檢查 `/Users/beanlin/.claude/skills/scheduled-task/` 是否存在
2. 確認有 `SKILL.md` 文件
3. 重新啟動 Claude Code

### Q: Usage 檢查一直失敗

**解決**:
- 等待 usage 降低
- 使用 `--max-usage=90` 調整閾值
- 減少批次處理的任務數量

## 安全性考量

1. **只在指定時間執行**: 防止在工作時間意外執行
2. **Usage 限制**: 防止超出 token 限制，自動暫停並重試
3. **Git 保護**:
   - 執行前自動 stash 未提交變更
   - Stash 後切換到最新的 dev branch
   - 從最新的 dev 創建 feature branch
   - 每個 Issue 獨立 branch，不會互相干擾
4. **智能錯誤處理**:
   - 自動嘗試多種解決方案
   - 持續推進，不輕易停止
   - 無法解決的問題會記錄在摘要中
5. **自動進入排程**: 任務拆解完成後直接進入排程，不詢問確認

---

## 🎯 開始使用

準備好讓 AI 在夜間自動完成你的開發任務了嗎？

```bash
/scheduled-task EK-995 EK-978
```

設定好排程，晚安，明天早上見！💤
