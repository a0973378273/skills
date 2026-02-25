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

使用工作描述：
```bash
/scheduled-task "實作深色模式切換功能"
```

添加多個任務：
```bash
/scheduled-task EK-995 EK-978 EK-980
```

## 核心功能

### 1. 📋 智能任務分析
- 自動獲取 Jira issue 詳細資訊
- 分析需求並拆解成可執行的 TODO 清單
- 支援多個 issue 或工作的批次處理
- 自動建立任務間的依賴關係

### 2. ⏰ 時間窗口控制
- **執行時間**: 只在晚上 21:00 - 早上 07:00 執行
- **自動等待**: 不在執行時間時自動進入等待狀態
- **智能恢復**: 到達執行時間後自動繼續
- **時區支援**: 使用本地時區（Asia/Taipei）

### 3. 📊 Usage 監控
- 執行前檢查 token usage 是否 < 80%
- Usage 過高時自動暫停並等待
- 每個任務執行前都會重新檢查
- 防止超出 token 限制

### 4. 🔄 Git 工作流程管理
- 執行前自動檢查 git 工作區狀態
- 工作區不乾淨時自動 stash
- 每完成一個 Jira issue 後：
  - 從 dev branch 創建新的 feature branch
  - 提交相關程式碼變更
  - 使用 Jira issue key 作為 branch 和 commit 前綴
- 自動處理 git 衝突和錯誤

### 5. 🎯 自動執行循環
每一輪執行都會：
1. ✅ 檢查當前時間是否在執行窗口內
2. ✅ 檢查 token usage 是否 < 80%
3. ✅ 檢查 git 工作區狀態
4. ✅ 執行當前任務
5. ✅ 創建 branch 並 commit
6. ✅ 進入下一輪循環

## 執行條件

所有任務執行前都會檢查以下條件：

| 條件 | 要求 | 不符合時的處理 |
|------|------|---------------|
| **執行時間** | 21:00 - 07:00 | 等待到 21:00 |
| **Token Usage** | < 80% | 暫停執行並提示 |
| **Git 狀態** | 工作區乾淨 | 自動 stash |

## 詳細執行流程

### 階段 1: 任務分析與規劃
```
📋 獲取 Jira Issue(s)
   ↓
🤔 分析需求
   ↓
✅ 拆解成 TODO 清單
   ↓
📝 創建任務排程（但不執行）
   ↓
⏱️ 直接進入排程（不詢問確認）
```

### 階段 2: 執行循環
```
對於每個 Jira Issue:
   ↓
⏰ 檢查時間 (21:00-07:00)
   ├─ 不在範圍 → ⏸️ 等待到 21:00
   └─ 在範圍 → 繼續
   ↓
📊 檢查 Usage < 80%
   ├─ 超過 80% → ⏸️ 暫停並通知用戶
   └─ 未超過 → 繼續
   ↓
🔍 檢查 Git 狀態
   ├─ 不乾淨 → 💾 自動 stash
   └─ 乾淨 → 繼續
   ↓
▶️ 執行該 Issue 的所有任務
   ↓
🌿 從 dev 創建 feature branch
   ↓
💾 提交程式碼變更
   ↓
✅ 標記該 Issue 完成
   ↓
⤴️ 返回檢查下一個 Issue
```

## 使用範例

### 範例 1: 單一 Jira Issue
```bash
/scheduled-task EK-995
```

**執行流程：**
```
1. 分析 EK-995
2. 拆解成 4 個 TODO
3. 創建排程並直接進入等待（不詢問確認）
4. 等待到晚上 21:00
5. 檢查 usage < 80%
6. 檢查 git 狀態並 stash（如需要）
7. 依序執行 4 個 TODO
8. 創建 feat/EK-995-xxx branch
9. Commit 變更
10. 完成
```

### 範例 2: 多個 Jira Issues
```bash
/scheduled-task EK-995 EK-978
```

**執行流程：**
```
1. 分析 EK-995 和 EK-978
2. 拆解成 8 個 TODO（4+4）
3. 創建排程，EK-978 依賴 EK-995
4. 直接進入排程（不詢問確認）

--- 第一輪：EK-995 ---
5. 等待到 21:00
6. 檢查 usage < 80%
7. 檢查 git 狀態
8. 執行 EK-995 的 4 個 TODO
9. 創建 feat/EK-995-xxx branch
10. Commit 變更

--- 第二輪：EK-978 ---
11. 再次檢查時間（仍在 21:00-07:00）
12. 再次檢查 usage < 80%
13. 再次檢查 git 狀態
14. 執行 EK-978 的 4 個 TODO
15. 創建 feat/EK-978-xxx branch
16. Commit 變更
17. 完成
```

### 範例 3: 自定義工作
```bash
/scheduled-task "重構網路層架構並添加快取機制"
```

**執行流程：**
```
1. 分析需求
2. 拆解成 TODO（例如 6 個任務）
3. 創建排程
4. 等待到 21:00
5. 逐一執行並 commit
```

## 時間窗口說明

### 執行時間窗口
- **開始時間**: 21:00 (晚上 9 點)
- **結束時間**: 07:00 (早上 7 點)
- **時區**: Asia/Taipei (台北時間)
- **跨日處理**: 自動處理跨日情況（21:00 → 次日 07:00）

### 時間檢查邏輯
```
當前時間 = 02:00
→ 在執行窗口內 ✅

當前時間 = 15:00
→ 不在執行窗口內 ❌
→ 等待到 21:00 (還需等待 6 小時)

當前時間 = 08:00
→ 不在執行窗口內 ❌
→ 等待到 21:00 (還需等待 13 小時)
```

## Usage 監控說明

### 檢查時機
- 每個 Jira issue 執行前
- 每個大型任務執行前
- 自動持續監控

### 計算方式
```
current_usage = (已使用 tokens / 總 token 限制) × 100%

if current_usage >= 80%:
    暫停執行
    通知用戶
    等待用戶確認是否繼續
else:
    繼續執行
```

### 處理策略
| Usage | 動作 |
|-------|------|
| < 80% | ✅ 正常執行 |
| 80% - 90% | ⚠️ 警告但繼續 |
| > 90% | 🛑 強制暫停 |

## Git 工作流程

### Branch 命名規則
```
feat/EK-XXX-{issue-summary-short}
```

**範例：**
- `feat/EK-995-fix-newcomer-bonus-timing`
- `feat/EK-978-fix-guest-task-page-navigation`

### Commit 訊息格式
```
[EK-XXX] {簡短描述}

{詳細說明}

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**範例：**
```
[EK-995] 修正新人獎勵時間驗證邏輯

- 在點擊登入按鈕時記錄活動期間狀態
- 修改 LoginViewModel 保存按鈕點擊時的活動狀態
- 在登入 API 呼叫時使用保存的活動狀態

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

### Stash 處理
```bash
# 檢查工作區狀態
git status

# 如果有未提交的變更
git stash push -m "Auto stash before scheduled task execution at {timestamp}"

# 執行任務...

# 任務完成後提示用戶是否恢復 stash
```

## 錯誤處理

### 執行過程中的錯誤
```
遇到錯誤時：
1. 暫停當前任務執行
2. 記錄錯誤詳情
3. 保留已完成的進度
4. 詢問用戶如何處理：
   - 跳過當前任務
   - 重試當前任務
   - 中止所有任務
```

### 常見錯誤處理

| 錯誤類型 | 處理方式 |
|---------|---------|
| Git 衝突 | 暫停並通知用戶手動解決 |
| API 失敗 | 重試 3 次，失敗後暫停 |
| 編譯錯誤 | 記錄錯誤並詢問是否繼續 |
| Token 超限 | 立即停止並保存進度 |

## 進度追蹤

### 執行狀態顯示
```
📊 排程任務執行狀態

總任務數: 2 個 Jira Issues (8 個 TODO)
已完成: 1 個 Issue (4 個 TODO)
進行中: 1 個 Issue (0/4 TODO)
等待中: 0 個 Issue

當前狀態: ⏸️ 等待執行時間窗口
下次執行: 今晚 21:00 (還需等待 3 小時 25 分鐘)

Token Usage: 45,123 / 200,000 (22.56%) ✅
```

### 任務清單
```
✅ EK-995: 修正新人獎勵時間驗證邏輯
   ✅ #1: 在點擊登入按鈕時記錄活動期間狀態
   ✅ #2: 修改 LoginViewModel 保存按鈕點擊時的活動狀態
   ✅ #3: 在登入 API 呼叫時使用保存的活動狀態
   ✅ #4: 測試驗證修正後的時序邏輯
   📦 Branch: feat/EK-995-fix-newcomer-bonus-timing
   💾 Commit: [EK-995] 修正新人獎勵時間驗證邏輯

⏳ EK-978: 修正訪客任務頁導航邏輯
   ⏸️ #5: 分析任務頁面的訪客檢查邏輯
   ⏸️ #6: 在所有任務頁按鈕添加訪客登入檢查
   ⏸️ #7: 修改 handleTodo 統一處理訪客跳轉邏輯
   ⏸️ #8: 測試訪客在任務頁的所有按鈕點擊
```

## 配置選項

可以在執行時調整以下選項：

### 時間設定
```bash
# 使用預設時間（21:00-07:00）
/scheduled-task EK-995

# 立即執行（跳過時間檢查，僅用於測試）
/scheduled-task EK-995 --now

# 自定義時間窗口
/scheduled-task EK-995 --start-time=22:00 --end-time=06:00
```

### Usage 設定
```bash
# 使用預設閾值（80%）
/scheduled-task EK-995

# 自定義 usage 閾值
/scheduled-task EK-995 --max-usage=70

# 忽略 usage 檢查（不推薦）
/scheduled-task EK-995 --ignore-usage
```

### Git 設定
```bash
# 自動 stash（預設）
/scheduled-task EK-995

# 禁止 stash，遇到不乾淨的工作區時中止
/scheduled-task EK-995 --no-stash

# 指定基礎 branch（預設為 dev）
/scheduled-task EK-995 --base-branch=main
```

## 與其他 Skills 的整合

### 搭配 jira-task
```bash
# 先用 scheduled-task 規劃
/scheduled-task EK-995 EK-978

# scheduled-task 內部會自動呼叫 jira-task 來分析需求
```

### 搭配 jira-pr
```bash
# 完成後自動創建 PR（可選）
/scheduled-task EK-995 --auto-pr
```

## 最佳實踐

### ✅ 建議做法
1. **批次處理**: 一次排程多個相關的 issues
2. **合理估計**: 確保任務能在一個夜晚完成
3. **監控進度**: 定期查看執行狀態
4. **保持簡單**: 複雜任務拆分成多個小 issues

### ❌ 避免的做法
1. **過度排程**: 排程過多任務導致無法在時間窗口內完成
2. **忽略錯誤**: 不處理執行過程中的錯誤
3. **強制執行**: 在 usage 過高時強制執行
4. **跳過檢查**: 使用 --now 或 --ignore-usage 在生產環境

## 故障排除

### Q: 任務一直在等待執行時間

**檢查：**
```bash
# 查看當前時間
date

# 確認時區設定
echo $TZ
```

**解決：**
- 確認當前時間是否在 21:00-07:00 之外
- 使用 `--now` 標誌立即執行（測試用）

### Q: Usage 檢查一直失敗

**檢查：**
```bash
# 查看當前 usage
/tasks  # 查看 token usage
```

**解決：**
- 等待 usage 降低
- 清理不必要的對話歷史
- 使用 `--max-usage` 調整閾值

### Q: Git stash 失敗

**檢查：**
```bash
git status
git stash list
```

**解決：**
- 手動 commit 或 stash 變更
- 使用 `--no-stash` 禁用自動 stash
- 確保 git 配置正確

### Q: Branch 創建失敗

**檢查：**
```bash
git branch -a
git remote -v
```

**解決：**
- 確認 dev branch 存在
- 使用 `--base-branch` 指定其他基礎 branch
- 檢查 git 權限

## 安全性考量

### 自動執行的安全措施
1. **只在指定時間執行**: 防止在工作時間意外執行
2. **Usage 限制**: 防止超出 token 限制
3. **Git 保護**: 自動 stash 防止丟失程式碼
4. **錯誤處理**: 遇到問題立即暫停
5. **自動進入排程**: 任務拆解完成後直接進入排程，不詢問確認

### 建議的審查流程
```
1. 排程任務前檢查 TODO 清單
2. 確認執行時間和條件
3. 隔天早上檢查執行結果
4. Review 生成的程式碼變更
5. 測試功能是否正常
6. 創建 PR 進行 code review
```

## 進階功能

### 通知機制（規劃中）
- 任務開始時通知
- 任務完成時通知
- 遇到錯誤時通知
- Usage 接近限制時警告

### 排程儲存（規劃中）
- 保存排程到本地檔案
- 支援跨 session 恢復
- 排程歷史記錄

### 並行執行（規劃中）
- 支援獨立任務並行執行
- 自動檢測任務依賴關係
- 智能資源分配

## 技術實現

此 skill 使用以下工具和技術：

1. **Jira MCP Server** - 獲取 issue 資訊
2. **TaskCreate/TaskUpdate/TaskList** - 管理 TODO 清單
3. **Bash** - 執行 git 命令和時間檢查
4. **Read/Write/Edit** - 程式碼操作
5. **定時檢查** - 循環檢查執行條件
6. **狀態管理** - 追蹤執行進度

## 版本歷史

### v1.0.0 (Current)
- ✅ 基本的排程執行功能
- ✅ 時間窗口控制
- ✅ Usage 監控
- ✅ Git 工作流程管理
- ✅ 多任務支援
- ✅ 錯誤處理

### 未來規劃
- 📋 通知機制
- 📋 排程儲存
- 📋 並行執行
- 📋 更智能的時間管理
- 📋 更詳細的執行報告

---

## 🎯 開始使用

準備好讓 AI 在夜間自動完成你的開發任務了嗎？

```bash
/scheduled-task <Jira Issue Key 或 URL>
```

晚安，明天早上見！💤
