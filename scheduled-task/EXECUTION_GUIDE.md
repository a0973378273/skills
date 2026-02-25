# 排程任務執行器 - 執行指南

這份文件定義了 scheduled-task skill 的具體執行邏輯和實作細節。

## 執行流程定義

### 階段 1: 初始化和任務分析

```
輸入: Jira Issue Key(s) 或工作描述
   ↓
1. 解析輸入參數
   - 識別 Jira Issue Keys
   - 識別 URL
   - 識別純文字工作描述
   ↓
2. 獲取 Jira Issue 詳細資訊（如適用）
   - 使用 mcp__jira__get_issue 獲取每個 issue
   - 提取 summary, description, priority 等
   ↓
3. 分析需求並拆解任務
   - 分析問題核心
   - 確認需要的資源
   - 使用 AskUserQuestion 確認不明確的需求
   ↓
4. 創建 TODO 清單
   - 使用 TaskCreate 創建所有任務
   - 設置任務間的依賴關係（TaskUpdate addBlockedBy）
   - 按 Jira Issue 分組任務
   ↓
5. 向用戶展示排程
   - 顯示所有任務清單
   - 顯示預計執行時間
   - 顯示執行條件
   ↓
6. 直接進入排程（不詢問用戶確認）
   - 任務拆解完成後自動進入排程等待執行時間
   - 用戶可以在任何時候手動中斷
```

### 階段 2: 執行循環

```
對於每個 Jira Issue（按順序）：

┌─────────────────────────────────────┐
│ 執行前檢查 (Pre-execution Checks)    │
└─────────────────────────────────────┘
   ↓
1. 時間檢查
   ├─ 獲取當前時間: date +"%H:%M"
   ├─ 檢查是否在 21:00-07:00 範圍內
   ├─ 如果不在範圍:
   │  ├─ 計算需等待時間
   │  ├─ 通知用戶
   │  └─ 等待或暫停
   └─ 如果在範圍: 繼續
   ↓
2. Usage 檢查（自動重試機制）
   ├─ 獲取當前 token usage
   ├─ 計算 usage 百分比
   ├─ 如果 >= 80%:
   │  ├─ 檢查是否在執行時間內（21:00-07:00）
   │  ├─ 如果在時間內:
   │  │  ├─ 通知用戶 usage 過高，自動暫停
   │  │  ├─ 暫停 1 小時
   │  │  ├─ 1 小時後重新檢查 usage
   │  │  │  ├─ 如果 < 80%: 繼續執行
   │  │  │  └─ 如果 >= 80%: 再次暫停 1 小時
   │  │  └─ 重複直到 usage < 80% 或超出執行時間
   │  └─ 如果超出時間: 中止執行並通知用戶
   └─ 如果 < 80%: 繼續
   ↓
3. Git 狀態檢查
   ├─ 執行: git status --porcelain
   ├─ 如果有未提交變更:
   │  ├─ 通知用戶需要 stash
   │  ├─ 執行: git stash push -m "Auto stash at {timestamp}"
   │  └─ 記錄 stash 資訊
   └─ 如果乾淨: 繼續
   ↓
4. 確保在正確的 branch
   ├─ 執行: git checkout dev
   ├─ 執行: git pull origin dev
   └─ 如果失敗: 通知用戶並暫停

┌─────────────────────────────────────┐
│ 任務執行 (Task Execution)            │
└─────────────────────────────────────┘
   ↓
5. 執行該 Issue 的所有 TODO
   對於每個 TODO:
   ├─ TaskUpdate 設置狀態為 in_progress
   ├─ 執行任務內容（讀取、修改、測試程式碼）
   ├─ 如果成功: TaskUpdate 設置為 completed
   └─ 如果失敗:
      ├─ 記錄錯誤
      ├─ 詢問用戶如何處理
      └─ 根據用戶選擇: 重試/跳過/中止
   ↓
6. 驗證變更
   ├─ 檢查程式碼變更: git diff
   ├─ 可選: 編譯檢查
   └─ 可選: 執行測試

┌─────────────────────────────────────┐
│ Git 提交 (Git Commit)                │
└─────────────────────────────────────┘
   ↓
7. 創建 feature branch
   ├─ 生成 branch 名稱: feat/{ISSUE-KEY}-{short-summary}
   ├─ 執行: git checkout -b {branch_name}
   └─ 如果失敗: 處理錯誤
   ↓
8. Stage 變更
   ├─ 執行: git add {modified_files}
   └─ 避免使用 git add -A（防止意外提交）
   ↓
9. Commit 變更
   ├─ 生成 commit 訊息:
   │  [ISSUE-KEY] {summary}
   │
   │  {詳細描述}
   │
   │  Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
   ├─ 執行: git commit -m "{message}"
   └─ 如果失敗: 處理錯誤
   ↓
10. 推送到 remote（可選）
    ├─ 執行: git push origin {branch_name}
    └─ 記錄 branch 資訊

┌─────────────────────────────────────┐
│ 完成當前 Issue (Issue Completion)   │
└─────────────────────────────────────┘
   ↓
11. 標記 Issue 完成
    ├─ 記錄完成時間
    ├─ 記錄 branch 名稱
    └─ 記錄 commit hash
    ↓
12. 顯示進度
    ├─ 更新進度報告
    └─ 顯示剩餘任務

┌─────────────────────────────────────┐
│ 準備下一輪 (Next Iteration)          │
└─────────────────────────────────────┘
   ↓
13. 檢查是否有更多 Issues
    ├─ 如果有: 返回步驟 1（執行前檢查）
    └─ 如果沒有: 進入完成階段
```

### 階段 3: 完成和總結

```
1. 顯示執行摘要
   ├─ 已完成的 Issues
   ├─ 創建的 branches
   ├─ 提交的 commits
   └─ 總執行時間
   ↓
2. 處理 stashed 變更（如有）
   ├─ 提示用戶有 stashed 變更
   └─ 詢問是否要恢復
   ↓
3. 提供後續建議
   ├─ 建議創建 PR
   ├─ 建議執行測試
   └─ 建議進行 code review
```

## 時間檢查實作

### 檢查當前時間是否在執行窗口內

```bash
#!/bin/bash

# 獲取當前小時（24小時制）
current_hour=$(date +"%H")

# 檢查是否在 21:00-07:00 範圍內
# 21:00-23:59 或 00:00-07:00
if [ $current_hour -ge 21 ] || [ $current_hour -lt 7 ]; then
    echo "在執行窗口內"
    exit 0
else
    echo "不在執行窗口內"
    exit 1
fi
```

### 計算需要等待的時間

```bash
#!/bin/bash

current_hour=$(date +"%H")

if [ $current_hour -ge 21 ]; then
    # 當前在 21:00-23:59，可以執行
    echo "0"
elif [ $current_hour -lt 7 ]; then
    # 當前在 00:00-06:59，可以執行
    echo "0"
else
    # 當前在 07:00-20:59，需要等待到 21:00
    hours_to_wait=$((21 - current_hour))
    echo "$hours_to_wait"
fi
```

## Usage 檢查實作（自動重試機制）

### 從系統訊息中提取 usage

使用系統提供的 token usage 資訊：
```
<system_warning>Token usage: 77019/200000; 122981 remaining</system_warning>
```

### 自動重試邏輯

```python
# 從系統訊息中提取
# "Token usage: {used}/{total}; {remaining} remaining"

used_tokens = 77019
total_tokens = 200000
usage_percentage = (used_tokens / total_tokens) * 100

if usage_percentage >= 80:
    # 檢查是否在執行時間內
    current_hour = get_current_hour()

    if is_within_execution_window(current_hour):
        # 在執行時間內（21:00-07:00），自動暫停並重試
        while usage_percentage >= 80:
            # 通知用戶
            print(f"⚠️ Usage 已達 {usage_percentage}%")
            print(f"⏸️ 暫停 1 小時，{next_check_time} 時重新檢查")

            # 暫停 1 小時
            wait(1 hour)

            # 重新檢查時間窗口
            current_hour = get_current_hour()
            if not is_within_execution_window(current_hour):
                # 超出執行時間，中止
                print("🛑 已超出執行時間窗口，中止執行")
                abort_execution()
                break

            # 重新檢查 usage
            usage_percentage = get_current_usage_percentage()

            if usage_percentage < 80:
                print(f"✅ Usage 已降至 {usage_percentage}%，繼續執行")
                break

        # 繼續執行
        continue_execution()
    else:
        # 超出執行時間，直接中止
        print("🛑 Usage 過高且超出執行時間，中止執行")
        abort_execution()
else:
    # Usage 正常，繼續執行
    continue_execution()
```

### 等待時間計算

```python
def wait_for_usage_decrease():
    """
    等待 usage 降低的邏輯

    Returns:
        bool: True 如果 usage 已降低，False 如果超時或超出執行窗口
    """
    max_retries = 10  # 最多等待 10 次（10 小時）
    retry_count = 0
    wait_interval = 3600  # 1 小時（秒）

    while retry_count < max_retries:
        # 檢查當前時間
        current_hour = get_current_hour()

        if not is_within_execution_window(current_hour):
            print(f"⏰ 當前時間 {current_hour}:00 超出執行窗口")
            return False

        # 暫停 1 小時
        retry_count += 1
        next_check_time = format_time(current_time + wait_interval)

        print(f"⏸️ 暫停中... ({retry_count}/{max_retries})")
        print(f"📅 下次檢查: {next_check_time}")

        sleep(wait_interval)

        # 重新檢查 usage
        usage_percentage = get_current_usage_percentage()

        print(f"📊 當前 usage: {usage_percentage}%")

        if usage_percentage < 80:
            print(f"✅ Usage 已降至安全範圍")
            return True

    print(f"⚠️ 已等待 {max_retries} 小時，usage 仍未降低")
    return False
```

### 執行時間窗口檢查

```python
def is_within_execution_window(hour: int) -> bool:
    """
    檢查是否在執行時間窗口內

    Args:
        hour: 當前小時（0-23）

    Returns:
        bool: True 如果在 21:00-07:00 範圍內
    """
    # 21:00-23:59 或 00:00-07:00
    return hour >= 21 or hour < 7
```

## Git 狀態檢查實作

### 檢查工作區是否乾淨

```bash
# 檢查是否有未提交的變更
if [ -n "$(git status --porcelain)" ]; then
    echo "工作區不乾淨"
    exit 1
else
    echo "工作區乾淨"
    exit 0
fi
```

### 自動 Stash

```bash
# 獲取當前時間戳
timestamp=$(date +"%Y-%m-%d_%H-%M-%S")

# Stash 變更
git stash push -m "Auto stash before scheduled task at $timestamp"

# 檢查 stash 是否成功
if [ $? -eq 0 ]; then
    echo "Stash 成功"
    # 記錄 stash ID
    stash_id=$(git stash list | head -n 1 | cut -d: -f1)
    echo "Stash ID: $stash_id"
else
    echo "Stash 失敗"
    exit 1
fi
```

## Branch 和 Commit 實作

### 生成 Branch 名稱

```
規則: feat/{ISSUE-KEY}-{short-summary}

範例:
- EK-995 "新人獎勵領取時間限制問題"
  → feat/EK-995-fix-newcomer-bonus-timing

- EK-978 "訪客任務頁導航錯誤"
  → feat/EK-978-fix-guest-task-navigation

生成邏輯:
1. 提取 Issue Key
2. 從 summary 提取關鍵字
3. 轉換為 kebab-case
4. 限制長度（最多 50 字符）
```

### 生成 Commit 訊息

```
格式:
[{ISSUE-KEY}] {一行摘要}

{詳細描述，每行最多 72 字符}

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>

範例:
[EK-995] 修正新人獎勵時間驗證邏輯

- 在點擊登入按鈕時記錄活動期間狀態
- 修改 LoginViewModel 保存按鈕點擊時的活動狀態
- 在登入 API 呼叫時使用保存的活動狀態
- 添加測試確保時序邏輯正確

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

### Git 命令序列

```bash
# 1. 確保在 dev branch
git checkout dev
git pull origin dev

# 2. 創建新 branch
branch_name="feat/EK-995-fix-newcomer-bonus-timing"
git checkout -b "$branch_name"

# 3. Stage 變更的文件
git add app/src/main/java/com/work/xux/want/presentation/feature/login/LoginViewModel.kt

# 4. Commit
git commit -m "[EK-995] 修正新人獎勵時間驗證邏輯

- 在點擊登入按鈕時記錄活動期間狀態
- 修改 LoginViewModel 保存按鈕點擊時的活動狀態
- 在登入 API 呼叫時使用保存的活動狀態

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

# 5. 推送到 remote（可選）
git push origin "$branch_name"
```

## 錯誤處理策略

### 時間窗口外執行

```
檢測: current_hour < 21 and current_hour >= 7

處理:
1. 計算需等待時間
2. 顯示訊息：
   "⏸️ 當前時間不在執行窗口內（21:00-07:00）
    現在時間: {current_time}
    下次執行: 今晚 21:00
    需等待: {hours} 小時 {minutes} 分鐘"
3. 選項：
   - 等待到執行時間（預設）
   - 立即執行（--now）
   - 取消排程
```

### Usage 超過限制

```
檢測: usage_percentage >= 80

處理:
1. 顯示訊息：
   "⚠️ Token Usage 已達 {usage_percentage}%
    已使用: {used_tokens:,}
    總限制: {total_tokens:,}
    剩餘: {remaining_tokens:,}

    為確保後續任務順利執行，建議暫停。"
2. 選項：
   - 暫停執行（推薦）
   - 繼續執行（風險：可能超出限制）
   - 取消所有任務
```

### Git 工作區不乾淨

```
檢測: git status --porcelain 有輸出

處理:
1. 列出未提交的變更
2. 顯示訊息：
   "📝 檢測到未提交的變更：
    {變更檔案列表}

    需要先處理這些變更才能執行任務。"
3. 選項：
   - 自動 stash（推薦）
   - 手動處理後繼續
   - 取消執行
```

### Git 操作失敗

```
可能的失敗：
- checkout 失敗
- branch 創建失敗
- commit 失敗
- push 失敗

處理:
1. 記錄錯誤訊息
2. 顯示具體錯誤
3. 提供解決建議
4. 選項：
   - 重試
   - 手動解決後繼續
   - 取消執行
```

### 任務執行失敗

```
可能的失敗：
- 檔案讀取錯誤
- 程式碼修改錯誤
- 編譯失敗
- 測試失敗

處理:
1. 記錄失敗的任務
2. 保留已完成的進度
3. 顯示錯誤詳情
4. 選項：
   - 重試當前任務
   - 跳過當前任務
   - 中止所有任務
```

## 進度追蹤和報告

### 執行狀態檔案（可選）

儲存位置: `/tmp/scheduled-task-{timestamp}.json`

```json
{
  "session_id": "scheduled-task-20260204-210000",
  "start_time": "2026-02-04T21:00:00+08:00",
  "status": "running",
  "issues": [
    {
      "key": "EK-995",
      "summary": "新人獎勵領取時間限制問題",
      "status": "completed",
      "tasks": [
        {
          "id": "1",
          "subject": "在點擊登入按鈕時記錄活動期間狀態",
          "status": "completed",
          "start_time": "2026-02-04T21:05:00+08:00",
          "end_time": "2026-02-04T21:12:00+08:00"
        }
      ],
      "branch": "feat/EK-995-fix-newcomer-bonus-timing",
      "commit": "abc123def456",
      "completion_time": "2026-02-04T21:45:00+08:00"
    }
  ],
  "stashes": [
    {
      "id": "stash@{0}",
      "message": "Auto stash before scheduled task at 2026-02-04_21-00-00"
    }
  ],
  "usage_snapshots": [
    {
      "time": "2026-02-04T21:00:00+08:00",
      "used": 45123,
      "total": 200000,
      "percentage": 22.56
    }
  ]
}
```

### 實時進度顯示

```
┌────────────────────────────────────────────────┐
│ 🌙 排程任務執行中                              │
├────────────────────────────────────────────────┤
│ 開始時間: 2026-02-04 21:00:00                  │
│ 當前時間: 2026-02-04 21:45:32                  │
│ 執行時長: 45 分鐘 32 秒                        │
├────────────────────────────────────────────────┤
│ 總進度: ████████████░░░░ 60% (2/4 Issues)     │
├────────────────────────────────────────────────┤
│ ✅ EK-995 (已完成)                             │
│    ├─ ✅ 記錄活動期間狀態                      │
│    ├─ ✅ 修改 LoginViewModel                   │
│    ├─ ✅ 使用保存的活動狀態                    │
│    └─ ✅ 測試時序邏輯                          │
│    📦 Branch: feat/EK-995-...                  │
│                                                │
│ ⏳ EK-978 (執行中)                             │
│    ├─ ✅ 分析訪客檢查邏輯                      │
│    ├─ ▶️  添加訪客登入檢查 (進行中)            │
│    ├─ ⏸️ 修改 handleTodo 邏輯                  │
│    └─ ⏸️ 測試訪客按鈕點擊                      │
│                                                │
│ ⏸️ EK-980 (等待中)                             │
│    └─ 等待 EK-978 完成                         │
├────────────────────────────────────────────────┤
│ Token Usage: 87,245 / 200,000 (43.62%) ✅     │
│ 時間檢查: ✅ 在執行窗口內 (至 07:00)           │
└────────────────────────────────────────────────┘
```

## 最終檢查清單

執行完成後的驗證：

```
✅ 所有任務都已完成
✅ 所有變更都已提交
✅ 所有 branches 都已創建
✅ Git 工作區恢復乾淨狀態
✅ Stashed 變更已記錄（如有）
✅ 執行報告已生成
✅ 沒有遺留的臨時檔案
```

## 用戶交互範例

### 開始執行

```
用戶: /scheduled-task EK-995 EK-978

助手:
📋 已分析 2 個 Jira Issues，拆解成 8 個 TODO 任務。

EK-995: 修正新人獎勵時間驗證邏輯 (4 個任務)
EK-978: 修正訪客任務頁導航邏輯 (4 個任務)

執行條件:
⏰ 時間窗口: 21:00 - 07:00
📊 Usage 限制: < 80%
🔄 Git 要求: 工作區乾淨

當前狀態:
⏰ 當前時間: 15:30 (不在執行窗口)
📊 Usage: 45,123 / 200,000 (22.56%) ✅
🔄 Git 狀態: 乾淨 ✅

排程將在今晚 21:00 開始執行。

是否確認此排程？
```

### 執行中提示

```
🌙 21:00 - 開始執行排程任務

✅ 時間檢查通過
✅ Usage 檢查通過 (22.56%)
✅ Git 狀態檢查通過

開始執行 EK-995...
```

### 完成總結

```
🎉 所有排程任務已完成！

執行摘要:
├─ 開始時間: 2026-02-04 21:00:00
├─ 結束時間: 2026-02-04 23:30:15
├─ 總耗時: 2 小時 30 分鐘
└─ Token Usage: 143,567 / 200,000 (71.78%)

已完成的 Issues:
✅ EK-995: 修正新人獎勵時間驗證邏輯
   📦 Branch: feat/EK-995-fix-newcomer-bonus-timing
   💾 Commit: abc123def

✅ EK-978: 修正訪客任務頁導航邏輯
   📦 Branch: feat/EK-978-fix-guest-task-navigation
   💾 Commit: def456ghi

📝 Stashed 變更:
stash@{0}: Auto stash before scheduled task at 2026-02-04_21-00-00

下一步建議:
1. 檢查程式碼變更
2. 執行測試
3. 創建 Pull Requests
4. 恢復 stashed 變更（如需要）
```

---

這份執行指南定義了 scheduled-task skill 的完整執行邏輯。
在實際實作時，請嚴格遵循這些流程以確保任務的正確和安全執行。
