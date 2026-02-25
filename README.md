# Claude Code Skills

這個目錄包含了項目的自定義 Claude Code skills。

## 📚 可用的 Skills

### `/jira-pr` - 從 Jira Issue 自動創建 PR

自動化從 Jira issue 到 Pull Request 的完整流程。

**快速使用：**
```bash
/jira-pr EK-907
```

**功能：**
- ✅ 自動獲取 Jira issue 資訊
- ✅ 創建符合規範的 git branch
- ✅ 智能分組並提交修改
- ✅ 推送到 GitHub
- ✅ 創建詳細的 Pull Request

**查看詳細文檔：**
- [SKILL.md](./jira-pr/SKILL.md) - Skill 完整說明
- [QUICKSTART.md](./jira-pr/QUICKSTART.md) - 快速開始指南

---

### `/jira-task` - Jira 任務自動實作

從 Jira issue 自動分析需求、列出 TODO 清單並依序完成任務。

**快速使用：**
```bash
/jira-task EK-920
```

**功能：**
- ✅ 自動分析 Jira issue 需求
- ✅ 主動提問確認細節和缺少的資源
- ✅ 創建結構化的 TODO 清單
- ✅ 依序執行並完成所有實作
- ✅ 驗證結果符合需求

**查看詳細文檔：**
- [SKILL.md](./jira-task/SKILL.md) - Skill 完整說明
- [QUICKSTART.md](./jira-task/QUICKSTART.md) - 快速開始指南
- [README.md](./jira-task/README.md) - 詳細文檔

---

### `/qa-release` - QA 版本自動發布

自動化 QA 版本發布的完整流程，從合併分支到 Firebase 部署。

**快速使用：**
```bash
/qa-release
```

**功能：**
- ✅ 自動合併 dev 到 QA branch
- ✅ 智能版本號管理（自動遞增）
- ✅ 更新 release notes
- ✅ Commit 並推送到遠端
- ✅ 建置並上傳到 Firebase App Distribution

**查看詳細文檔：**
- [SKILL.md](./qa-release/SKILL.md) - Skill 完整說明
- [QUICKSTART.md](./qa-release/QUICKSTART.md) - 快速開始指南

---

## 🚀 如何使用 Skills

1. **輸入斜杠命令**
   ```bash
   /jira-pr
   ```

2. **查看可用 skills**

   在對話中輸入：
   ```
   What skills are available?
   ```

3. **獲取 skill 幫助**
   ```
   How do I use /jira-pr?
   ```

---

## 📖 Skill 開發指南

### 創建新的 Skill

1. **創建 skill 目錄**
   ```bash
   mkdir -p .claude/skills/my-skill
   ```

2. **創建 SKILL.md 文件**

   `.claude/skills/my-skill/SKILL.md`:
   ```markdown
   ---
   name: my-skill
   description: 簡短描述這個 skill 的功能和使用場景
   ---

   # Skill 標題

   詳細說明...

   ## 使用方法
   ...
   ```

3. **重要格式要求**
   - ✅ 文件名必須是 `SKILL.md`（大小寫敏感）
   - ✅ 必須有 YAML frontmatter（`---` 包圍的元數據）
   - ✅ `name` 和 `description` 字段是必需的
   - ✅ Description 應該清楚說明何時使用這個 skill

4. **測試 skill**
   ```bash
   # Skills 會自動重新加載
   # 在 Claude Code 中測試
   /my-skill
   ```

### Skill 文件結構

```
.claude/skills/
├── README.md                    # 總覽文檔（你正在閱讀）
└── jira-pr/                     # Skill 目錄
    ├── SKILL.md                 # ⭐ Skill 定義（必需）
    ├── README.md                # 詳細說明文檔（可選）
    └── QUICKSTART.md            # 快速開始指南（可選）
```

### YAML Frontmatter 示例

```yaml
---
name: my-skill
description: 當需要執行 X 任務時使用。包括 Y 功能和 Z 能力。適合處理 A、B、C 場景。
---
```

**好的 description：**
- ✅ 說明功能：「從 Jira issue 自動創建 PR 到 dev branch」
- ✅ 列出能力：「包括獲取 issue 信息、創建 branch、智能提交」
- ✅ 明確場景：「當需要處理 Jira issue、創建 PR 時使用」

**不好的 description：**
- ❌ 太簡短：「創建 PR」
- ❌ 太模糊：「處理 git 相關任務」
- ❌ 缺少場景：「自動化工作流」

---

## 🔍 Skill 發現機制

Claude Code 會自動掃描以下位置的 skills：

1. **企業級** - 由管理員配置（優先級最高）
2. **個人級** - `~/.claude/skills/`
3. **項目級** - `.claude/skills/`（本項目）
4. **插件級** - 安裝的插件提供

**優先級：** 企業 > 個人 > 項目 > 插件

---

## ⚙️ 調試 Skills

### 檢查 Skill 是否被加載

在 Claude Code 中詢問：
```
What skills are available?
```

或查看具體 skill：
```
Show me the jira-pr skill
```

### 常見問題

#### Skill 沒有出現

1. **檢查文件名**
   ```bash
   ls -la .claude/skills/jira-pr/
   # 應該看到 SKILL.md（注意大小寫）
   ```

2. **檢查 YAML frontmatter**
   ```bash
   head -5 .claude/skills/jira-pr/SKILL.md
   # 應該以 --- 開頭
   ```

3. **重啟 Claude Code**
   ```bash
   # 退出並重新啟動 Claude Code
   ```

#### Skill 執行失敗

- 檢查 skill 中使用的工具是否可用（如 `gh` CLI、Jira MCP server）
- 查看錯誤訊息並調整 skill 邏輯
- 確認前置條件都已滿足

---

## 📚 相關資源

- [Claude Code Skills 官方文檔](https://code.claude.com/docs/en/skills.md)
- [Slash Commands 文檔](https://code.claude.com/docs/en/slash-commands.md)
- [本項目 Skills](./jira-pr/SKILL.md)

---

## 💡 最佳實踐

1. **清晰的命名**
   - 使用描述性的 skill 名稱
   - 避免與內建命令衝突

2. **詳細的文檔**
   - 在 SKILL.md 中提供完整示例
   - 說明前置條件和預期結果
   - 包含故障排除指南

3. **用戶友好**
   - 提供清晰的錯誤訊息
   - 支持多種輸入格式
   - 給出有用的提示

4. **自動化優先**
   - 減少用戶需要手動操作的步驟
   - 智能處理邊緣情況
   - 提供合理的預設值

---

**開始使用你的第一個 skill：**

```bash
/jira-pr EK-907
```
