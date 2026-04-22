---
name: create-jira-bug-issue
description: 解析 QA 回報的 Bug 文字，自動擷取設備資訊、情境敘述、目前情況、預期情況，建立 Jira Bug issue。自動設定標籤 Android、Sprint 為 bug pool、影響版本從文字中擷取、受託人為自己。適合用於快速將 QA 回報轉成 Jira Bug ticket。
---

# Jira Bug 快速建立

從 QA 回報的文字中自動解析資訊並建立 Jira Bug issue。

## 快速使用

直接貼上 QA 回報文字：
```bash
/jira-bug 【設備】Samsung Galaxy S24 Android 14
版本 1.2.3
進入個人頁面後點擊收藏 tab，頁面無反應。
目前情況：點擊收藏 tab 沒有切換頁面
預期情況：應該要切換到收藏頁面
```

也可以不帶參數，會提示你輸入：
```bash
/jira-bug
```

## 執行流程

### 1. 解析輸入文字

從輸入文字中智能擷取以下四個欄位：

| 欄位 | 說明 | 解析策略 |
|------|------|---------|
| **設備資訊** | 裝置型號、OS 版本 | 尋找「設備」「裝置」「手機」「機型」等關鍵字，或辨識裝置型號名稱（如 Samsung、Pixel、OPPO 等） |
| **情境敘述** | 重現步驟、操作流程 | 輸入文字中描述操作流程的部分，排除設備、目前情況、預期情況後的敘述內容 |
| **目前情況** | Bug 的實際行為 | 尋找「目前」「實際」「結果」「現況」「現在」等關鍵字後的內容 |
| **預期情況** | 正確的預期行為 | 尋找「預期」「應該」「期望」「正確」等關鍵字後的內容 |

### 2. 擷取影響版本

從輸入文字中辨識版本號，常見格式：
- `版本 1.2.3`、`v1.2.3`、`Version 1.2.3`
- `1.2.3 版`、`版號 1.2.3`
- 純數字版本格式如 `1.2.3`、`2.0.1`

**重要：Jira 中的版本名稱格式為 `Android X.X.X`**（例如 `Android 1.2.3`）。
從文字中擷取到版本號後，需加上 `Android ` 前綴才能對應到 Jira 的版本。

### 3. 辨識附圖

檢查輸入中是否包含圖片（截圖、螢幕錄影截圖等）。圖片來源可能是：
- 使用者在對話中直接貼上的圖片（會出現在 image-cache 路徑，如 `/Users/beanlin/.claude/image-cache/...`）
- 輸入文字中提及的 `[Image #N]` 標記，對應的圖片路徑會在 `[Image source: ...]` 中

如果有圖片，記錄所有圖片的本地檔案路徑，在確認解析結果時一併顯示圖片數量，並在 issue 建立後上傳為附件。

### 4. 向使用者確認解析結果

在建立 Jira issue 之前，**必須**先向使用者展示解析結果並確認：

```
📋 解析結果：

📱 設備資訊：Samsung Galaxy S24 / Android 14
📝 情境敘述：進入個人頁面後點擊收藏 tab，頁面無反應
🔴 目前情況：點擊收藏 tab 沒有切換頁面
🟢 預期情況：應該要切換到收藏頁面
📌 影響版本：1.2.3
📌 標題建議：[Android] 個人頁面收藏 tab 點擊無反應
📎 附圖：2 張

請確認以上資訊是否正確？如需修改請告知。
```

**重要**：必須等待使用者確認後才能建立 issue。

### 5. 建立 Jira Bug Issue

使用 `mcp__jira-extended__jira_create_issue` 建立 issue：

- **projectKey**: `EK`
- **issueType**: `漏洞`
- **summary**: `[Android] {根據情境敘述和目前情況產生的簡潔標題}`
- **description**: 格式化的 Bug 描述（見下方模板）
- **fields**:
  - `labels`: `["Android"]`
  - `customfield_10020`: Sprint「bug pool」的 ID = `268`
  - `versions`: 影響版本，格式為 `[{"name": "Android X.X.X"}]`
  - `assignee`: 當前使用者（`{"accountId": "712020:a914dba3-7c1a-4da3-b55e-6df1f8d36bc5"}`）

### 6. Description 模板

建立 issue 時使用以下 description 格式：

```
h3. 設備資訊
{設備資訊}

h3. 情境敘述
{情境敘述}

h3. 目前情況
{目前情況}

h3. 預期情況
{預期情況}
```

### 7. 上傳附圖到 Jira

如果步驟 3 中辨識到有圖片，在 issue 建立完成後，使用 Jira REST API 上傳附件：

```bash
curl -s -X POST \
  -H "X-Atlassian-Token: no-check" \
  -H "Authorization: Basic $(echo -n "$JIRA_EMAIL:$JIRA_API_TOKEN" | base64)" \
  -F "file=@{圖片本地路徑}" \
  "https://showyouapp.atlassian.net/rest/api/2/issue/{issueKey}/attachments"
```

**認證資訊取得方式**：
- 從環境變數 `JIRA_EMAIL` 和 `JIRA_API_TOKEN` 取得
- 如果環境變數不存在，嘗試從 `~/.claude/.env` 或 `~/.env` 讀取

**多張圖片**：逐一上傳每張圖片，每張圖片一次 curl 請求。

**上傳失敗處理**：如果上傳失敗，告知使用者手動上傳，不要阻斷整個流程。

### 8. 建立完成後輸出

Issue 建立完成後，**必須**輸出 Jira 連結和欄位摘要：

```
✅ Issue 已建立：EK-XXXX
🔗 https://showyouapp.atlassian.net/browse/EK-XXXX

- **標題**：[Android] ...
- **標籤**：Android
- **Sprint**：bug pool
- **影響版本**：Android X.X.X
- **受託人**：bean.lin
- **附圖**：2 張已上傳 ✅（如有附圖時顯示）
```

**Jira 連結格式**：`https://showyouapp.atlassian.net/browse/{issueKey}`

## 完整示例

### 示例 1：標準 QA 回報

輸入：
```
/jira-bug 設備：OPPO Reno10 Pro Android 13
版本 2.1.0
步驟：
1. 開啟 App
2. 進入直播間
3. 發送留言
目前情況：留言發送後畫面卡住約 3 秒
預期情況：留言應立即顯示在聊天室中
```

解析結果：
- 📱 設備資訊：OPPO Reno10 Pro / Android 13
- 📝 情境敘述：1. 開啟 App → 2. 進入直播間 → 3. 發送留言
- 🔴 目前情況：留言發送後畫面卡住約 3 秒
- 🟢 預期情況：留言應立即顯示在聊天室中
- 📌 影響版本：2.1.0
- 📌 標題：[Android] 直播間發送留言後畫面卡住

### 示例 2：非結構化回報

輸入：
```
/jira-bug 用 Pixel 8 Pro (Android 14) 測 1.9.5 版，在商品頁面按加入購物車，按鈕沒反應，應該要跳出加入成功的提示
```

解析結果：
- 📱 設備資訊：Pixel 8 Pro / Android 14
- 📝 情境敘述：在商品頁面按加入購物車按鈕
- 🔴 目前情況：按鈕沒反應
- 🟢 預期情況：應該要跳出加入成功的提示
- 📌 影響版本：1.9.5
- 📌 標題：[Android] 商品頁面加入購物車按鈕無反應

### 示例 3：缺少部分資訊

輸入：
```
/jira-bug 1.8.0 版，首頁 banner 圖片沒有顯示
```

解析結果（會提問缺少的資訊）：
```
📋 解析結果：

📱 設備資訊：❌ 未提供（請補充測試裝置型號和 Android 版本）
📝 情境敘述：開啟 App 首頁查看 banner
🔴 目前情況：首頁 banner 圖片沒有顯示
🟢 預期情況：❌ 未明確說明（建議：首頁 banner 應正常顯示圖片）
📌 影響版本：1.8.0

❓ 請補充以下資訊：
1. 測試裝置型號和 Android 版本？
2. 預期情況的描述是否為「首頁 banner 應正常顯示圖片」？
```

## 欄位設定說明

| 欄位 | 值 | 說明 |
|------|-----|------|
| 專案 | EK | 固定為 EK 專案 |
| Issue 類型 | 漏洞 | Bug 類型在此專案中的名稱 |
| 標籤 | Android | 固定標籤 |
| Sprint | bug pool | 固定放入 bug pool Sprint |
| 影響版本 | 從文字擷取 | 自動辨識版本號 |
| 受託人 | 自己 | accountId: `712020:a914dba3-7c1a-4da3-b55e-6df1f8d36bc5` (bean.lin) |
| Summary | 自動產生 | 格式：`[Android] {簡潔描述}` |

## 注意事項

### Sprint 設定
- Sprint 欄位為 `customfield_10020`
- **Bug Pool 的 Sprint ID = `268`**
- 需要使用 Sprint ID（數字），不是名稱
- 建立 issue 時無法直接設定 Sprint，需先建立 issue 再用 `mcp__jira-extended__jira_update_issue` 更新

### 影響版本設定
- 影響版本（Affects Version）的欄位名稱是 `versions`
- **Jira 中版本名稱格式為 `Android X.X.X`**（例如 `Android 1.2.3`）
- 格式為：`[{"name": "Android 1.2.3"}]`
- 從輸入文字擷取版本號後，自動加上 `Android ` 前綴
- 如果文字中找不到版本號，**必須詢問使用者**

### 標題生成規則
- 固定前綴 `[Android]`
- 簡潔描述問題核心（15-30 字）
- 避免包含版本號或裝置資訊（這些放在 description 中）

## 故障排除

### Q: 無法設定 Sprint
Sprint 欄位可能需要特定的 Sprint ID。解決方式：
1. 先建立 issue（不含 Sprint）
2. 使用 `mcp__jira-extended__jira_update_issue` 單獨設定 Sprint

### Q: 影響版本不存在
如果 Jira 專案中尚未建立該版本，建立 issue 時可能會失敗。解決方式：
1. 先不設定影響版本
2. 告知使用者需要在 Jira 中先建立該版本

### Q: 解析結果不準確
- 向使用者展示解析結果
- 讓使用者修改後再建立 issue
- 下次可以使用更結構化的格式回報

## 技術實現

此 skill 使用以下工具：

1. **Jira MCP Server (`jira-extended`)** - 建立 issue
   - `mcp__jira-extended__jira_create_issue` - 建立 Bug issue
   - `mcp__jira-extended__jira_update_issue` - 補充設定 Sprint 等欄位
2. **Bash (curl)** - 上傳附件到 Jira（Jira REST API `/rest/api/2/issue/{issueKey}/attachments`）
3. **AskUserQuestion** - 確認解析結果、補充缺少的資訊
