# Compose 組件生成器 - 快速開始

> 5 分鐘學會使用 `/compose` skill 創建 Compose 組件

## 🎯 第一步：了解組件類型

### Widget/Card（簡單組件）
適合：按鈕、卡片、圖標、無狀態 UI

```bash
/compose UserAvatarCard
```

### Screen/Page（完整頁面）
適合：完整頁面、需要業務邏輯

```bash
/compose ProfileScreen --with-viewmodel
```

## ⚡ 基礎用法

### 1. 創建簡單的 Card 組件

```bash
/compose ProductCard
```

**生成的文件**：`com/work/compose/components/ProductCard.kt`

**包含內容**：
- ✅ Composable 函數
- ✅ 參數定義
- ✅ @Preview 預覽
- ✅ KDoc 註釋

**立即可用**：
```kotlin
@Composable
fun ProductCard(
    productName: String,
    price: String,
    imageUrl: String,
    modifier: Modifier = Modifier
) {
    // 自動生成的實作...
}

@Preview
@Composable
private fun ProductCardPreview() {
    ProductCard(
        productName = "Sample Product",
        price = "$99.99",
        imageUrl = "https://example.com/image.jpg"
    )
}
```

### 2. 創建完整的 Screen

```bash
/compose OrderHistoryScreen --with-viewmodel
```

**生成 5 個文件**：

#### OrderHistoryUiState.kt
```kotlin
data class OrderHistoryUiState(
    val orders: List<Order> = emptyList(),
    val isLoading: Boolean = false
)
```

#### OrderHistoryUiEvent.kt
```kotlin
sealed class OrderHistoryUiEvent {
    object LoadOrders : OrderHistoryUiEvent()
    object Refresh : OrderHistoryUiEvent()
    data class OrderClick(val orderId: String) : OrderHistoryUiEvent()
    data class CancelOrder(val orderId: String) : OrderHistoryUiEvent()
}
```

#### OrderHistoryUiEffect.kt
```kotlin
sealed class OrderHistoryUiEffect {
    data class ShowToast(val message: String) : OrderHistoryUiEffect()
    data class NavigateToOrderDetail(val orderId: String) : OrderHistoryUiEffect()
    data class ShowError(val error: String) : OrderHistoryUiEffect()
}
```

#### OrderHistoryViewModel.kt
```kotlin
@HiltViewModel
class OrderHistoryViewModel @Inject constructor(
    private val orderUseCase: OrderUseCase
) : ViewModel() {

    private val _uiState = MutableStateFlow(OrderHistoryUiState())
    val uiState: StateFlow<OrderHistoryUiState> = _uiState

    private val _uiEffect = Channel<OrderHistoryUiEffect>()
    val uiEffect = _uiEffect.receiveAsFlow()

    init {
        onEvent(OrderHistoryUiEvent.LoadOrders)
    }

    fun onEvent(event: OrderHistoryUiEvent) {
        when (event) {
            OrderHistoryUiEvent.LoadOrders -> loadOrders()
            OrderHistoryUiEvent.Refresh -> refresh()
            is OrderHistoryUiEvent.OrderClick -> handleOrderClick(event.orderId)
            is OrderHistoryUiEvent.CancelOrder -> cancelOrder(event.orderId)
        }
    }

    private fun loadOrders() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            try {
                orderUseCase.getOrders()
                    .onSuccess { orders, _ ->
                        _uiState.update {
                            it.copy(
                                orders = orders,
                                isLoading = false
                            )
                        }
                    }
                    .onError { code, message ->
                        _uiEffect.send(OrderHistoryUiEffect.ShowError(message))
                        _uiState.update { it.copy(isLoading = false) }
                    }
            } catch (e: Exception) {
                _uiEffect.send(OrderHistoryUiEffect.ShowError("載入失敗"))
                _uiState.update { it.copy(isLoading = false) }
            }
        }
    }

    private fun refresh() {
        loadOrders()
    }

    private fun handleOrderClick(orderId: String) {
        viewModelScope.launch {
            _uiEffect.send(OrderHistoryUiEffect.NavigateToOrderDetail(orderId))
        }
    }

    private fun cancelOrder(orderId: String) {
        viewModelScope.launch {
            // 取消訂單邏輯
            _uiEffect.send(OrderHistoryUiEffect.ShowToast("訂單已取消"))
        }
    }
}
```

#### OrderHistoryScreen.kt
```kotlin
@Composable
fun OrderHistoryScreen(
    viewModel: OrderHistoryViewModel = hiltViewModel(),
    onNavigateToDetail: (String) -> Unit = {},
    modifier: Modifier = Modifier
) {
    val uiState by viewModel.uiState.collectAsState()
    val context = LocalContext.current

    // 處理 Effect
    LaunchedEffect(Unit) {
        viewModel.uiEffect.collectLatest { effect ->
            when (effect) {
                is OrderHistoryUiEffect.ShowToast -> {
                    Toast.makeText(context, effect.message, Toast.LENGTH_SHORT).show()
                }
                is OrderHistoryUiEffect.NavigateToOrderDetail -> {
                    onNavigateToDetail(effect.orderId)
                }
                is OrderHistoryUiEffect.ShowError -> {
                    Toast.makeText(context, effect.error, Toast.LENGTH_LONG).show()
                }
            }
        }
    }

    OrderHistoryContent(
        uiState = uiState,
        onEvent = viewModel::onEvent,
        modifier = modifier
    )
}
```

## 🔥 實戰範例

### 範例 1：用戶資料卡片

**需求**：創建一個顯示用戶資訊的卡片

```bash
/compose UserInfoCard
```

**對話流程**：
```
我：/compose UserInfoCard

Claude：我來幫你創建 UserInfoCard 組件。

請提供組件參數（一行一個，按 Enter 結束）：

你：userName: String
你：email: String
你：avatarUrl: String
你：onEditClick: () -> Unit
你：（Enter 結束）

Claude：✅ 已創建 UserInfoCard.kt
       包含 4 個參數和 2 個 Preview
```

**生成的預覽**：
- Default Preview - 預設狀態
- Long Text Preview - 長文字測試

### 範例 2：登入頁面

**需求**：創建完整的登入頁面，包含表單驗證

```bash
/compose LoginScreen --with-viewmodel
```

**生成結構**：
```
presentation/feature/login/
├── LoginScreen.kt          # UI 組件
├── LoginUiState.kt         # 狀態定義
├── LoginUiEvent.kt         # 用戶事件
├── LoginUiEffect.kt        # 副作用
└── LoginViewModel.kt       # 業務邏輯
```

**LoginUiState.kt**：
```kotlin
data class LoginUiState(
    val email: String = "",
    val password: String = "",
    val isLoading: Boolean = false,
    val isEmailValid: Boolean = true,
    val isPasswordValid: Boolean = true
)
```

**LoginUiEvent.kt**：
```kotlin
sealed class LoginUiEvent {
    data class EmailChange(val email: String) : LoginUiEvent()
    data class PasswordChange(val password: String) : LoginUiEvent()
    object LoginClick : LoginUiEvent()
    object ForgotPasswordClick : LoginUiEvent()
}
```

**LoginUiEffect.kt**：
```kotlin
sealed class LoginUiEffect {
    object NavigateToHome : LoginUiEffect()
    object NavigateToForgotPassword : LoginUiEffect()
    data class ShowError(val message: String) : LoginUiEffect()
    data class ShowToast(val message: String) : LoginUiEffect()
}
```

**LoginViewModel.kt**：
```kotlin
@HiltViewModel
class LoginViewModel @Inject constructor(
    private val authUseCase: AuthUseCase
) : ViewModel() {

    private val _uiState = MutableStateFlow(LoginUiState())
    val uiState: StateFlow<LoginUiState> = _uiState

    private val _uiEffect = Channel<LoginUiEffect>()
    val uiEffect = _uiEffect.receiveAsFlow()

    fun onEvent(event: LoginUiEvent) {
        when (event) {
            is LoginUiEvent.EmailChange -> updateEmail(event.email)
            is LoginUiEvent.PasswordChange -> updatePassword(event.password)
            LoginUiEvent.LoginClick -> login()
            LoginUiEvent.ForgotPasswordClick -> navigateToForgotPassword()
        }
    }

    private fun updateEmail(email: String) {
        _uiState.update {
            it.copy(
                email = email,
                isEmailValid = isValidEmail(email)
            )
        }
    }

    private fun updatePassword(password: String) {
        _uiState.update {
            it.copy(
                password = password,
                isPasswordValid = password.length >= 6
            )
        }
    }

    private fun login() {
        if (!validateInputs()) {
            return
        }

        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            try {
                authUseCase.login(
                    email = _uiState.value.email,
                    password = _uiState.value.password
                )
                    .onSuccess { user, _ ->
                        _uiState.update { it.copy(isLoading = false) }
                        _uiEffect.send(LoginUiEffect.NavigateToHome)
                    }
                    .onError { code, message ->
                        _uiState.update { it.copy(isLoading = false) }
                        _uiEffect.send(LoginUiEffect.ShowError(message))
                    }
            } catch (e: Exception) {
                _uiState.update { it.copy(isLoading = false) }
                _uiEffect.send(LoginUiEffect.ShowError("登入失敗"))
            }
        }
    }

    private fun navigateToForgotPassword() {
        viewModelScope.launch {
            _uiEffect.send(LoginUiEffect.NavigateToForgotPassword)
        }
    }

    private fun validateInputs(): Boolean {
        val currentState = _uiState.value

        if (!currentState.isEmailValid || currentState.email.isEmpty()) {
            viewModelScope.launch {
                _uiEffect.send(LoginUiEffect.ShowToast("請輸入有效的電子郵件"))
            }
            return false
        }

        if (!currentState.isPasswordValid || currentState.password.isEmpty()) {
            viewModelScope.launch {
                _uiEffect.send(LoginUiEffect.ShowToast("密碼至少需要 6 個字元"))
            }
            return false
        }

        return true
    }

    private fun isValidEmail(email: String): Boolean {
        return android.util.Patterns.EMAIL_ADDRESS.matcher(email).matches()
    }
}
```

### 範例 3：倒計時橫幅

**需求**：創建一個帶倒計時的促銷橫幅

```bash
/compose PromoBanner --widget
```

**生成的組件**：
```kotlin
@Composable
fun PromoBanner(
    title: String,
    remainingTimeSeconds: Long,
    onClaimClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    var timeLeft by remember { mutableStateOf(remainingTimeSeconds) }

    LaunchedEffect(remainingTimeSeconds) {
        timeLeft = remainingTimeSeconds
        while (timeLeft > 0) {
            delay(1.seconds)
            timeLeft--
        }
    }

    val hours = timeLeft / 3600
    val minutes = (timeLeft % 3600) / 60
    val seconds = timeLeft % 60

    Card(modifier = modifier.fillMaxWidth()) {
        Row(
            modifier = Modifier.padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Column {
                Text(text = title)
                Text(
                    text = String.format("%02d:%02d:%02d", hours, minutes, seconds),
                    style = MaterialTheme.typography.headlineMedium
                )
            }
            Button(onClick = onClaimClick) {
                Text("領取")
            }
        }
    }
}
```

## 📋 參數類型參考

### 常用參數類型

```kotlin
// 基礎類型
userName: String
age: Int
isActive: Boolean
score: Double

// 可空類型
email: String?
errorMessage: String?

// 默認值
isEnabled: Boolean = true
count: Int = 0

// Modifier
modifier: Modifier = Modifier

// 回調函數
onClick: () -> Unit
onItemClick: (Item) -> Unit
onTextChange: (String) -> Unit

// 數據類型
user: User
items: List<Item>

// Compose 類型
textStyle: TextStyle = MaterialTheme.typography.bodyMedium
backgroundColor: Color = Color.White
```

## 🎨 Preview 技巧

### 1. 多種狀態 Preview

```kotlin
// 空狀態
@Preview(showBackground = true, name = "Empty")
@Composable
private fun ScreenEmptyPreview() {
    ScreenContent(uiState = ScreenUiState(items = emptyList()))
}

// 載入中
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
            errorMessage = "無法載入資料"
        )
    )
}

// 成功狀態（有資料）
@Preview(showBackground = true, name = "Success")
@Composable
private fun ScreenSuccessPreview() {
    ScreenContent(
        uiState = ScreenUiState(
            items = listOf(
                Item("Item 1"),
                Item("Item 2"),
                Item("Item 3")
            )
        )
    )
}
```

### 2. 不同設備 Preview

```kotlin
// 手機
@Preview(
    name = "Phone",
    device = Devices.PIXEL_4,
    showSystemUi = true
)
@Composable
private fun PhonePreview() { ... }

// 平板
@Preview(
    name = "Tablet",
    device = Devices.PIXEL_C,
    showSystemUi = true
)
@Composable
private fun TabletPreview() { ... }
```

### 3. 深色模式 Preview

```kotlin
@Preview(
    name = "Light Mode",
    showBackground = true,
    uiMode = Configuration.UI_MODE_NIGHT_NO
)
@Composable
private fun LightPreview() { ... }

@Preview(
    name = "Dark Mode",
    showBackground = true,
    uiMode = Configuration.UI_MODE_NIGHT_YES
)
@Composable
private fun DarkPreview() { ... }
```

## ⚙️ 進階選項

### 自訂 Package 路徑

```bash
# 創建在 auth 模組中
/compose LoginButton --package com.work.compose.auth

# 創建在 payment 功能中
/compose PaymentCard --package com.work.xux.want.presentation.feature.payment
```

### 指定存放位置

Skill 會根據組件類型自動判斷位置：

| 組件名稱包含 | 存放位置 |
|-------------|---------|
| Screen, Page | `presentation/feature/{name}` |
| Card, Button, Banner | `compose/components` |
| Dialog, BottomSheet | `presentation/widget` |

## 🐛 疑難排解

### Q: 找不到生成的文件？

檢查 Android Studio 的 Project 視圖是否設置為 "Android"，切換到 "Project" 視圖查看完整目錄結構。

### Q: Import 錯誤？

生成的文件可能需要同步 Gradle：
```
File -> Sync Project with Gradle Files
```

### Q: Preview 不顯示？

1. 確認 Compose 版本 >= 1.0
2. 重建項目：`Build -> Rebuild Project`
3. 清除快取：`File -> Invalidate Caches / Restart`

### Q: ViewModel 注入失敗？

確認 dependencies：
```gradle
implementation "androidx.hilt:hilt-navigation-compose:1.0.0"
implementation "com.google.dagger:hilt-android:2.44"
kapt "com.google.dagger:hilt-compiler:2.44"
```

## 📚 下一步

### 學習更多

- 閱讀 [完整文檔](./SKILL.md)
- 查看 [範例組件](../../../app/src/main/java/com/work/compose/components/)
- 學習 [MVI 架構模式](./README.md#-架構模式)

### 開始創建

現在開始創建你的第一個組件：

```bash
/compose MyFirstCard
```

### 需要幫助？

在對話中詢問：
```
How do I create a Compose component with state management?
Show me examples of Preview usage
What's the difference between Widget and Screen?
```

---

**祝你編碼愉快！** 🎉
