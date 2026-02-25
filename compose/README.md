# Compose 組件生成器

> 自動創建符合 MVI 架構的 Jetpack Compose 組件

## 📋 功能特色

✅ **自動生成組件** - 一鍵創建 Composable 函數
✅ **@Preview 支援** - 自動生成多種預覽狀態
✅ **MVI 架構** - 完整的 State、Event、Effect 模式
✅ **ViewModel 生成** - 自動創建 UiState、UiEvent、UiEffect 和 ViewModel
✅ **智能判斷** - 根據命名自動判斷組件類型
✅ **完整註釋** - 生成 KDoc 風格的文檔註釋

## 🚀 快速開始

### 創建簡單組件

```bash
/compose UserAvatarCard
```

這會創建一個簡單的 Card 組件，包含：
- ✅ Composable 函數
- ✅ @Preview 預覽
- ✅ 完整註釋

### 創建完整 Screen

```bash
/compose ProfileSettingsScreen --with-viewmodel
```

這會創建一個完整的 Screen，包含：
- ✅ Composable UI
- ✅ UiState data class
- ✅ ViewModel with StateFlow
- ✅ 多種 Preview 狀態

### 互動式創建

```bash
/compose
```

會引導你完成：
1. 輸入組件名稱
2. 選擇組件類型
3. 設定參數
4. 選擇存放位置

## 📦 組件類型

### 1. Widget/Card（簡單組件）

適合：UI 組件、可複用元素、無狀態展示

**範例**：
- `UserAvatarCard` - 用戶頭像卡片
- `WelcomeBonusBanner` - 歡迎橫幅
- `CountdownTimer` - 倒計時組件

**生成內容**：
```
com/work/compose/components/
└── UserAvatarCard.kt
```

### 2. Screen/Page（完整頁面）

適合：完整頁面、需要狀態管理、業務邏輯

**範例**：
- `LoginScreen` - 登入頁面
- `ProfileSettingsScreen` - 個人資料設定
- `NotificationListScreen` - 通知列表

**生成內容**：
```
presentation/feature/login/
├── LoginScreen.kt
├── LoginUiState.kt
├── LoginUiEvent.kt
├── LoginUiEffect.kt
└── LoginViewModel.kt
```

## 🎯 使用場景

### 場景 1：快速原型設計

需要快速驗證 UI 設計：

```bash
/compose ProductCard
```

立即獲得可預覽的組件，開始迭代設計。

### 場景 2：新功能開發

開發新的功能頁面：

```bash
/compose OrderHistoryScreen --with-viewmodel
```

獲得完整的 MVI 架構模板，專注於業務邏輯。

### 場景 3：重構現有代碼

將 XML View 遷移到 Compose：

```bash
/compose UserProfileCard --widget
```

快速創建對應的 Compose 組件。

## 📐 架構模式

### MVI (Model-View-Intent) 架構

```
┌─────────────────────────────────────┐
│           Composable UI             │
│  (UserProfileScreen.kt)             │
└──────────────┬──────────────────────┘
               │ sends Events
               ▼
┌─────────────────────────────────────┐
│          ViewModel                  │
│  (UserProfileViewModel.kt)          │
│                                     │
│  ┌─────────────────────────────┐   │
│  │  onEvent(UiEvent)           │   │
│  └─────────────────────────────┘   │
│           │                         │
│           ▼                         │
│  ┌─────────────────────────────┐   │
│  │  Update State               │   │
│  │  Execute Business Logic     │   │
│  │  Send Effects               │   │
│  └─────────────────────────────┘   │
│           │                         │
└───────────┼─────────────────────────┘
            │
            ├─────► StateFlow<UiState> ──► UI observes
            │
            └─────► Flow<UiEffect> ──────► UI consumes
```

### 生成的程式碼結構

```kotlin
// UiState.kt - 定義 UI 狀態
data class ScreenUiState(
    val data: List<Item> = emptyList(),
    val isLoading: Boolean = false
)

// UiEvent.kt - 定義用戶事件
sealed class ScreenUiEvent {
    data class ItemClick(val item: Item) : ScreenUiEvent()
    object Refresh : ScreenUiEvent()
    data class DeleteItem(val id: String) : ScreenUiEvent()
}

// UiEffect.kt - 定義副作用
sealed class ScreenUiEffect {
    data class ShowToast(val message: String) : ScreenUiEffect()
    data class NavigateToDetail(val id: String) : ScreenUiEffect()
    object NavigateBack : ScreenUiEffect()
}

// ViewModel.kt - 狀態管理和業務邏輯
@HiltViewModel
class ScreenViewModel @Inject constructor(
    private val useCase: UseCase
) : ViewModel() {
    private val _uiState = MutableStateFlow(ScreenUiState())
    val uiState: StateFlow<ScreenUiState> = _uiState

    private val _uiEffect = Channel<ScreenUiEffect>()
    val uiEffect = _uiEffect.receiveAsFlow()

    fun onEvent(event: ScreenUiEvent) {
        when (event) {
            is ScreenUiEvent.ItemClick -> handleItemClick(event.item)
            ScreenUiEvent.Refresh -> refresh()
            is ScreenUiEvent.DeleteItem -> deleteItem(event.id)
        }
    }

    private fun handleItemClick(item: Item) { ... }
    private fun refresh() { ... }
    private fun deleteItem(id: String) {
        viewModelScope.launch {
            // 業務邏輯
            _uiEffect.send(ScreenUiEffect.ShowToast("刪除成功"))
        }
    }
}

// Screen.kt - UI 組件
@Composable
fun Screen(
    viewModel: ScreenViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    val context = LocalContext.current

    // 處理 Effect
    LaunchedEffect(Unit) {
        viewModel.uiEffect.collectLatest { effect ->
            when (effect) {
                is ScreenUiEffect.ShowToast -> {
                    Toast.makeText(context, effect.message, Toast.LENGTH_SHORT).show()
                }
                is ScreenUiEffect.NavigateToDetail -> {
                    // 導航邏輯
                }
                ScreenUiEffect.NavigateBack -> {
                    // 返回邏輯
                }
            }
        }
    }

    ScreenContent(
        uiState = uiState,
        onEvent = viewModel::onEvent
    )
}
```

## 🎨 Preview 最佳實踐

生成的組件包含多種 Preview 狀態：

```kotlin
// 預設狀態
@Preview(showBackground = true, name = "Default")
@Composable
private fun ScreenDefaultPreview() {
    ScreenContent(uiState = ScreenUiState())
}

// 載入狀態
@Preview(showBackground = true, name = "Loading")
@Composable
private fun ScreenLoadingPreview() {
    ScreenContent(uiState = ScreenUiState(isLoading = true))
}

// 錯誤狀態
@Preview(showBackground = true, name = "Error")
@Composable
private fun ScreenErrorPreview() {
    ScreenContent(
        uiState = ScreenUiState(
            errorMessage = "發生錯誤"
        )
    )
}

// 數據狀態
@Preview(showBackground = true, name = "With Data")
@Composable
private fun ScreenDataPreview() {
    ScreenContent(
        uiState = ScreenUiState(
            data = listOf(/* sample data */)
        )
    )
}
```

## 📚 命名規範

### 組件命名

| 類型 | 命名模式 | 範例 |
|------|---------|------|
| Screen | `{Name}Screen` | `LoginScreen`, `ProfileScreen` |
| Card | `{Name}Card` | `UserCard`, `ProductCard` |
| Banner | `{Name}Banner` | `WelcomeBanner`, `PromoBanner` |
| Dialog | `{Name}Dialog` | `ConfirmDialog`, `ErrorDialog` |
| Bottom Sheet | `{Name}BottomSheet` | `FilterBottomSheet` |
| Custom Widget | `{Name}Widget` | `CountdownWidget` |

### Package 規範

| 組件類型 | Package 路徑 |
|---------|-------------|
| 共用組件 | `com.work.compose.components` |
| 功能組件 | `com.work.xux.want.presentation.feature.{feature}` |
| Widget | `com.work.xux.want.presentation.widget` |

## 🔧 自訂選項

### 指定組件類型

```bash
# 強制創建為 Widget（不含 ViewModel）
/compose MyComponent --widget

# 強制創建 ViewModel
/compose MyComponent --with-viewmodel
```

### 自訂 Package

```bash
/compose LoginButton --package com.work.compose.auth
```

### 指定參數

在互動模式中，可以指定組件參數：

```
參數 1: userName: String
參數 2: onProfileClick: () -> Unit
參數 3: isFollowing: Boolean = false
```

## 💡 提示與技巧

### 1. 組件分層

複雜組件應該拆分：

```kotlin
@Composable
fun ComplexCard() {
    Column {
        CardHeader()    // 私有子組件
        CardContent()   // 私有子組件
        CardFooter()    // 私有子組件
    }
}

@Composable
private fun CardHeader() { ... }

@Composable
private fun CardContent() { ... }

@Composable
private fun CardFooter() { ... }
```

### 2. 狀態提升

將狀態提升到父組件：

```kotlin
// ❌ 不推薦：狀態在子組件中
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }
    Button(onClick = { count++ }) {
        Text("Count: $count")
    }
}

// ✅ 推薦：狀態提升
@Composable
fun Counter(
    count: Int,
    onIncrement: () -> Unit
) {
    Button(onClick = onIncrement) {
        Text("Count: $count")
    }
}
```

### 3. Preview 參數化

使用 PreviewParameter 創建多種 Preview：

```kotlin
@Preview(showBackground = true)
@Composable
fun CardPreview(
    @PreviewParameter(CardStateProvider::class) state: CardState
) {
    MyCard(state = state)
}

class CardStateProvider : PreviewParameterProvider<CardState> {
    override val values = sequenceOf(
        CardState.Loading,
        CardState.Success(data),
        CardState.Error("錯誤訊息")
    )
}
```

## 🐛 常見問題

### Q: ViewModel 注入失敗？

**解決方案**：
```kotlin
// 確保添加 @HiltViewModel
@HiltViewModel
class MyViewModel @Inject constructor(...) : ViewModel()

// 在 Application 類中添加 @HiltAndroidApp
@HiltAndroidApp
class MyApp : Application()
```

### Q: Preview 無法顯示？

**解決方案**：
1. 確認 `@Preview` 註解正確
2. Preview 函數必須是 private 或 internal
3. 檢查是否有語法錯誤

### Q: StateFlow 不更新 UI？

**解決方案**：
```kotlin
// ✅ 正確：使用 collectAsState()
val uiState by viewModel.uiState.collectAsState()

// ❌ 錯誤：直接使用 value
val uiState = viewModel.uiState.value
```

## 🔗 相關資源

- [SKILL.md](./SKILL.md) - 完整 Skill 說明
- [QUICKSTART.md](./QUICKSTART.md) - 快速開始指南
- [Jetpack Compose 官方文檔](https://developer.android.com/jetpack/compose)
- [MVI 架構指南](https://developer.android.com/topic/architecture)

## 📝 更新日誌

### v1.0.0
- ✨ 初始版本
- ✅ 支援創建 Widget 和 Screen
- ✅ 自動生成 MVI 架構
- ✅ 多種 Preview 狀態
- ✅ 完整的 KDoc 註釋
