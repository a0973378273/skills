---
name: compose
description: 創建符合 MVI 架構的 Jetpack Compose 組件。自動生成 @Preview，按需創建 State、Event、Effect、ViewModel。當需要創建新的 Compose UI 組件、Screen、Widget 時使用此 skill。
---

# Compose 組件生成器

自動創建符合 MVI 架構的 Jetpack Compose 組件，包括 @Preview，並按需創建 State、Event、Effect、ViewModel。

## 快速使用

創建簡單組件（不需要 ViewModel）：
```bash
/compose UserAvatarCard
```

創建完整 Screen（包含 ViewModel）：
```bash
/compose ProfileSettingsScreen --with-viewmodel
```

互動式創建：
```bash
/compose
```

## 執行流程

當你執行這個 skill 時，我會自動完成以下步驟：

### 1. 收集組件資訊
- 組件名稱（如：`UserProfileCard`、`LoginScreen`）
- 組件類型：
  - **Widget/Card** - 簡單 UI 組件，不需要 ViewModel
  - **Screen/Page** - 完整頁面，需要 ViewModel 和狀態管理
- 組件參數（如：`userName: String`, `onClickAction: () -> Unit`）
- 存放位置（預設自動判斷）

### 2. 創建 Compose 組件文件
- 生成主要 Composable 函數
- 添加完整的 KDoc 註釋
- 創建多個 @Preview（預設狀態、不同場景、邊界情況）
- 如果組件複雜，拆分為私有子組件

### 3. 創建 State、Event、Effect（僅在需要時）
**重要**：只有在組件確實需要狀態管理時才創建這些文件。簡單的展示組件不需要。

如果組件需要狀態管理，按需創建以下文件：

**{ComponentName}State.kt** - UI 狀態（有狀態需要管理時才創建）
```kotlin
data class ProfileSettingsState(
    val userName: String = "",
    val email: String = "",
    val isLoading: Boolean = false
)
```

**{ComponentName}Event.kt** - 用戶事件（需要處理用戶交互時才創建）
```kotlin
sealed class ProfileSettingsEvent {
    data class UpdateUserName(val name: String) : ProfileSettingsEvent()
    data class UpdateEmail(val email: String) : ProfileSettingsEvent()
    object SaveSettings : ProfileSettingsEvent()
    object Refresh : ProfileSettingsEvent()
}
```

**{ComponentName}Effect.kt** - 一次性副作用（需要處理導航、Toast 等副作用時才創建）
```kotlin
sealed class ProfileSettingsEffect {
    data class ShowToast(val message: String) : ProfileSettingsEffect()
    object NavigateBack : ProfileSettingsEffect()
    data class NavigateToDetail(val userId: String) : ProfileSettingsEffect()
    data class ShowError(val error: String) : ProfileSettingsEffect()
}
```

### 4. 創建 ViewModel（僅在需要時）
**重要**：只有在組件需要業務邏輯處理時才創建 ViewModel。

如果組件是 Screen 且需要處理業務邏輯，創建 `{ComponentName}ViewModel.kt`：
```kotlin
@HiltViewModel
class ProfileSettingsViewModel @Inject constructor(
    private val userUseCase: UserUseCase
) : ViewModel() {

    private val _state = MutableStateFlow(ProfileSettingsState())
    val state: StateFlow<ProfileSettingsState> = _state

    private val _effect = Channel<ProfileSettingsEffect>()
    val effect = _effect.receiveAsFlow()

    fun onEvent(event: ProfileSettingsEvent) {
        when (event) {
            is ProfileSettingsEvent.UpdateUserName -> updateUserName(event.name)
            is ProfileSettingsEvent.UpdateEmail -> updateEmail(event.email)
            ProfileSettingsEvent.SaveSettings -> saveSettings()
            ProfileSettingsEvent.Refresh -> refresh()
        }
    }

    private fun updateUserName(name: String) {
        _state.update { it.copy(userName = name) }
    }

    private fun updateEmail(email: String) {
        _state.update { it.copy(email = email) }
    }

    private fun saveSettings() {
        viewModelScope.launch {
            _state.update { it.copy(isLoading = true) }
            // 業務邏輯...
            _effect.send(ProfileSettingsEffect.ShowToast("儲存成功"))
            _state.update { it.copy(isLoading = false) }
        }
    }

    private fun refresh() {
        // 刷新邏輯...
    }
}
```

### 5. 遵循 MVI 架構
- **State**: 使用 `StateFlow` 管理 UI 狀態
- **Event**: 使用 sealed class 處理用戶事件
- **Effect**: 使用 `Channel` + `Flow` 處理一次性副作用（導航、Toast）

## 組件類型

### Widget/Card（簡單組件）
適合：
- UI 組件（Button、Card、Avatar）
- 無狀態展示組件
- 可複用的小組件

**生成文件**：
- `{ComponentName}.kt` - Compose 組件 + @Preview

**範例**：
```kotlin
@Composable
fun UserAvatarCard(
    userName: String,
    avatarUrl: String,
    modifier: Modifier = Modifier
) {
    // 組件實作...
}

@Preview
@Composable
private fun UserAvatarCardPreview() {
    UserAvatarCard(
        userName = "John Doe",
        avatarUrl = "https://example.com/avatar.jpg"
    )
}
```

### Screen/Page（完整頁面）
適合：
- 完整的頁面或功能
- 需要狀態管理
- 需要業務邏輯處理

**生成文件**（按需創建）：
- `{ScreenName}.kt` - Compose UI（必須）
- `{ScreenName}State.kt` - UI 狀態（有狀態才創建）
- `{ScreenName}Event.kt` - 用戶事件（有交互才創建）
- `{ScreenName}Effect.kt` - 副作用（有副作用才創建）
- `{ScreenName}ViewModel.kt` - ViewModel（有業務邏輯才創建）

**範例結構**：
```
presentation/
└── feature/
    └── profile_settings/
        ├── ProfileSettingsScreen.kt
        ├── ProfileSettingsState.kt       # 按需創建
        ├── ProfileSettingsEvent.kt       # 按需創建
        ├── ProfileSettingsEffect.kt      # 按需創建
        └── ProfileSettingsViewModel.kt   # 按需創建
```

## 參數說明

| 參數 | 類型 | 必填 | 說明 | 示例 |
|-----|------|------|------|------|
| 組件名稱 | String | 是 | PascalCase 命名 | `UserProfileCard`, `LoginScreen` |
| --with-viewmodel | Flag | 否 | 強制創建 ViewModel | `--with-viewmodel` |
| --widget | Flag | 否 | 指定為簡單組件（不創建 ViewModel） | `--widget` |
| --package | String | 否 | 自定義 package 路徑 | `--package com.work.compose.auth` |

## 命名規則

### 組件命名
- **Widget/Card**: `{Name}Card`, `{Name}Button`, `{Name}Banner`
  - 範例：`UserAvatarCard`, `WelcomeBonusBanner`
- **Screen**: `{Name}Screen`, `{Name}Page`
  - 範例：`ProfileSettingsScreen`, `LoginScreen`

### 文件位置
- **共用組件**: `com.work.compose.components`
- **功能組件**: `com.work.xux.want.presentation.feature.{feature_name}`
- **Widget**: `com.work.xux.want.presentation.widget`

## 完整示例

### 示例 1：創建簡單的 Card 組件

```bash
/compose UserStatsCard
```

**生成的文件**：`com/work/compose/components/UserStatsCard.kt`

```kotlin
package com.work.compose.components

import androidx.compose.foundation.layout.*
import androidx.compose.material3.Card
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp

/**
 * UserStatsCard 組件 - 使用者統計卡片
 *
 * @param postsCount 貼文數量
 * @param followersCount 追蹤者數量
 * @param modifier 修飾符
 */
@Composable
fun UserStatsCard(
    postsCount: Int,
    followersCount: Int,
    modifier: Modifier = Modifier
) {
    Card(modifier = modifier.fillMaxWidth()) {
        Row(
            modifier = Modifier.padding(16.dp),
            horizontalArrangement = Arrangement.SpaceEvenly
        ) {
            StatItem(label = "貼文", count = postsCount)
            StatItem(label = "追蹤者", count = followersCount)
        }
    }
}

@Composable
private fun StatItem(
    label: String,
    count: Int,
    modifier: Modifier = Modifier
) {
    Column(modifier = modifier) {
        Text(text = count.toString())
        Text(text = label)
    }
}

@Preview(showBackground = true)
@Composable
private fun UserStatsCardPreview() {
    UserStatsCard(
        postsCount = 42,
        followersCount = 1234
    )
}

@Preview(showBackground = true, name = "Large Numbers")
@Composable
private fun UserStatsCardLargePreview() {
    UserStatsCard(
        postsCount = 99999,
        followersCount = 1000000
    )
}
```

### 示例 2：創建完整的 Screen

```bash
/compose NotificationSettingsScreen --with-viewmodel
```

**生成的文件**（根據需要創建）：
1. `NotificationSettingsScreen.kt`
2. `NotificationSettingsState.kt`（有狀態時才創建）
3. `NotificationSettingsEvent.kt`（有事件時才創建）
4. `NotificationSettingsEffect.kt`（有副作用時才創建）
5. `NotificationSettingsViewModel.kt`（有業務邏輯時才創建）

**NotificationSettingsState.kt**：
```kotlin
package com.work.xux.want.presentation.feature.notification_settings

data class NotificationSettingsState(
    val pushEnabled: Boolean = true,
    val emailEnabled: Boolean = false,
    val isLoading: Boolean = false
)
```

**NotificationSettingsEvent.kt**：
```kotlin
package com.work.xux.want.presentation.feature.notification_settings

sealed class NotificationSettingsEvent {
    data class TogglePushNotifications(val enabled: Boolean) : NotificationSettingsEvent()
    data class ToggleEmailNotifications(val enabled: Boolean) : NotificationSettingsEvent()
    object LoadSettings : NotificationSettingsEvent()
    object SaveSettings : NotificationSettingsEvent()
}
```

**NotificationSettingsEffect.kt**：
```kotlin
package com.work.xux.want.presentation.feature.notification_settings

sealed class NotificationSettingsEffect {
    data class ShowToast(val message: String) : NotificationSettingsEffect()
    data class ShowError(val error: String) : NotificationSettingsEffect()
    object NavigateBack : NotificationSettingsEffect()
}
```

**NotificationSettingsViewModel.kt**：
```kotlin
package com.work.xux.want.presentation.feature.notification_settings

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.work.xux.want.domain.usecase.SettingsUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.receiveAsFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import timber.log.Timber
import javax.inject.Inject

@HiltViewModel
class NotificationSettingsViewModel @Inject constructor(
    private val settingsUseCase: SettingsUseCase
) : ViewModel() {

    private val _state = MutableStateFlow(NotificationSettingsState())
    val state: StateFlow<NotificationSettingsState> = _state

    private val _effect = Channel<NotificationSettingsEffect>()
    val effect = _effect.receiveAsFlow()

    init {
        onEvent(NotificationSettingsEvent.LoadSettings)
    }

    fun onEvent(event: NotificationSettingsEvent) {
        when (event) {
            is NotificationSettingsEvent.TogglePushNotifications -> {
                togglePushNotifications(event.enabled)
            }
            is NotificationSettingsEvent.ToggleEmailNotifications -> {
                toggleEmailNotifications(event.enabled)
            }
            NotificationSettingsEvent.LoadSettings -> loadSettings()
            NotificationSettingsEvent.SaveSettings -> saveSettings()
        }
    }

    private fun loadSettings() {
        viewModelScope.launch {
            _state.update { it.copy(isLoading = true) }
            try {
                // TODO: 載入設定邏輯
                settingsUseCase.getNotificationSettings()
                    .onSuccess { settings, _ ->
                        _state.update {
                            it.copy(
                                pushEnabled = settings.pushEnabled,
                                emailEnabled = settings.emailEnabled,
                                isLoading = false
                            )
                        }
                    }
                    .onError { code, message ->
                        Timber.e("載入設定失敗: $code, $message")
                        _effect.send(NotificationSettingsEffect.ShowError(message))
                        _state.update { it.copy(isLoading = false) }
                    }
            } catch (e: Exception) {
                Timber.e(e, "載入設定異常")
                _effect.send(NotificationSettingsEffect.ShowError("載入失敗"))
                _state.update { it.copy(isLoading = false) }
            }
        }
    }

    private fun togglePushNotifications(enabled: Boolean) {
        _state.update { it.copy(pushEnabled = enabled) }
        saveSettings()
    }

    private fun toggleEmailNotifications(enabled: Boolean) {
        _state.update { it.copy(emailEnabled = enabled) }
        saveSettings()
    }

    private fun saveSettings() {
        viewModelScope.launch {
            try {
                // TODO: 儲存設定邏輯
                val currentState = _state.value
                settingsUseCase.saveNotificationSettings(
                    pushEnabled = currentState.pushEnabled,
                    emailEnabled = currentState.emailEnabled
                )
                    .onSuccess { _, _ ->
                        _effect.send(NotificationSettingsEffect.ShowToast("儲存成功"))
                    }
                    .onError { code, message ->
                        Timber.e("儲存設定失敗: $code, $message")
                        _effect.send(NotificationSettingsEffect.ShowError(message))
                    }
            } catch (e: Exception) {
                Timber.e(e, "儲存設定異常")
                _effect.send(NotificationSettingsEffect.ShowError("儲存失敗"))
            }
        }
    }
}
```

**NotificationSettingsScreen.kt**：
```kotlin
package com.work.xux.want.presentation.feature.notification_settings

import android.widget.Toast
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import kotlinx.coroutines.flow.collectLatest

/**
 * NotificationSettingsScreen - 通知設定頁面
 *
 * @param viewModel ViewModel
 * @param onNavigateBack 返回導航回調
 * @param modifier 修飾符
 */
@Composable
fun NotificationSettingsScreen(
    viewModel: NotificationSettingsViewModel = hiltViewModel(),
    onNavigateBack: () -> Unit = {},
    modifier: Modifier = Modifier
) {
    val state by viewModel.state.collectAsState()
    val context = LocalContext.current

    // 處理 Effect
    LaunchedEffect(Unit) {
        viewModel.effect.collectLatest { effect ->
            when (effect) {
                is NotificationSettingsEffect.ShowToast -> {
                    Toast.makeText(context, effect.message, Toast.LENGTH_SHORT).show()
                }
                is NotificationSettingsEffect.ShowError -> {
                    Toast.makeText(context, effect.error, Toast.LENGTH_LONG).show()
                }
                NotificationSettingsEffect.NavigateBack -> {
                    onNavigateBack()
                }
            }
        }
    }

    NotificationSettingsContent(
        state = state,
        onEvent = viewModel::onEvent,
        modifier = modifier
    )
}

@Composable
private fun NotificationSettingsContent(
    state: NotificationSettingsState,
    onEvent: (NotificationSettingsEvent) -> Unit,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Text(
            text = "通知設定",
            style = MaterialTheme.typography.headlineMedium
        )

        Spacer(modifier = Modifier.height(16.dp))

        SettingRow(
            title = "推播通知",
            enabled = state.pushEnabled,
            onToggle = { enabled ->
                onEvent(NotificationSettingsEvent.TogglePushNotifications(enabled))
            }
        )

        SettingRow(
            title = "電子郵件通知",
            enabled = state.emailEnabled,
            onToggle = { enabled ->
                onEvent(NotificationSettingsEvent.ToggleEmailNotifications(enabled))
            }
        )

        if (state.isLoading) {
            CircularProgressIndicator(
                modifier = Modifier.align(Alignment.CenterHorizontally)
            )
        }
    }
}

@Composable
private fun SettingRow(
    title: String,
    enabled: Boolean,
    onToggle: (Boolean) -> Unit,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier
            .fillMaxWidth()
            .padding(vertical = 8.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(text = title)
        Switch(
            checked = enabled,
            onCheckedChange = onToggle
        )
    }
}

@Preview(showBackground = true)
@Composable
private fun NotificationSettingsScreenPreview() {
    NotificationSettingsContent(
        state = NotificationSettingsState(
            pushEnabled = true,
            emailEnabled = false
        ),
        onEvent = {}
    )
}

@Preview(showBackground = true, name = "Loading State")
@Composable
private fun NotificationSettingsScreenLoadingPreview() {
    NotificationSettingsContent(
        state = NotificationSettingsState(
            isLoading = true
        ),
        onEvent = {}
    )
}
```

## MVI 架構最佳實踐

### 1. State 設計
```kotlin
data class ScreenState(
    // 數據狀態
    val items: List<Item> = emptyList(),
    val selectedItem: Item? = null,

    // UI 狀態
    val isLoading: Boolean = false,
    val isRefreshing: Boolean = false
)
```

**注意**：不要在 State 中放置一次性事件（如錯誤訊息、Toast），應該使用 Effect。

### 2. Event 處理
使用 sealed class 定義所有用戶事件：
```kotlin
sealed class ScreenEvent {
    data class ItemClick(val item: Item) : ScreenEvent()
    object Refresh : ScreenEvent()
    object Retry : ScreenEvent()
    data class SearchQueryChange(val query: String) : ScreenEvent()
    data class ToggleFavorite(val itemId: String) : ScreenEvent()
}
```

在 ViewModel 中統一處理：
```kotlin
fun onEvent(event: ScreenEvent) {
    when (event) {
        is ScreenEvent.ItemClick -> handleItemClick(event.item)
        ScreenEvent.Refresh -> refresh()
        ScreenEvent.Retry -> retry()
        is ScreenEvent.SearchQueryChange -> updateSearchQuery(event.query)
        is ScreenEvent.ToggleFavorite -> toggleFavorite(event.itemId)
    }
}
```

### 3. Effect 處理
使用 Channel + Flow 處理一次性副作用：
```kotlin
// 定義 Effect
sealed class ScreenEffect {
    data class ShowToast(val message: String) : ScreenEffect()
    data class ShowSnackbar(val message: String) : ScreenEffect()
    object NavigateBack : ScreenEffect()
    data class NavigateToDetail(val id: String) : ScreenEffect()
    data class ShowError(val error: String) : ScreenEffect()
}

// 在 ViewModel 中發送 Effect
private val _effect = Channel<ScreenEffect>()
val effect = _effect.receiveAsFlow()

viewModelScope.launch {
    _effect.send(ScreenEffect.ShowToast("操作成功"))
}

// 在 Composable 中處理 Effect
LaunchedEffect(Unit) {
    viewModel.effect.collectLatest { effect ->
        when (effect) {
            is ScreenEffect.ShowToast -> {
                Toast.makeText(context, effect.message, Toast.LENGTH_SHORT).show()
            }
            is ScreenEffect.ShowSnackbar -> {
                snackbarHostState.showSnackbar(effect.message)
            }
            ScreenEffect.NavigateBack -> {
                navController.navigateUp()
            }
            is ScreenEffect.NavigateToDetail -> {
                navController.navigate("detail/${effect.id}")
            }
            is ScreenEffect.ShowError -> {
                // 顯示錯誤對話框
            }
        }
    }
}
```

**為什麼使用 Channel 而不是 StateFlow？**
- Channel 確保每個 Effect 只被消費一次
- StateFlow 可能會在配置變更時重複觸發
- Channel 適合一次性事件（導航、Toast）

### 4. Preview 設計
創建多個 Preview 展示不同狀態：
```kotlin
@Preview(showBackground = true, name = "Default")
@Composable
private fun ScreenDefaultPreview() { ... }

@Preview(showBackground = true, name = "Loading")
@Composable
private fun ScreenLoadingPreview() { ... }

@Preview(showBackground = true, name = "Error")
@Composable
private fun ScreenErrorPreview() { ... }

@Preview(showBackground = true, name = "Empty")
@Composable
private fun ScreenEmptyPreview() { ... }
```

## 前置條件

執行此 skill 前請確保：
- ✅ 使用 Jetpack Compose
- ✅ 已設置 Hilt 依賴注入（如需 ViewModel）
- ✅ 項目遵循 MVI 架構模式（State、Event、Effect）
- ✅ 添加必要的 Compose 和 ViewModel 依賴

## 故障排除

### Q: 如何決定是否需要 ViewModel？

**建議**：
- **不需要 ViewModel**：純展示組件、可複用的 UI 元素、無狀態組件
- **需要 ViewModel**：完整頁面、需要業務邏輯、需要狀態管理、需要 API 調用

### Q: 組件應該放在哪個 package？

**建議**：
- **共用組件** → `com.work.compose.components`
- **功能特定組件** → `com.work.xux.want.presentation.feature.{feature_name}`
- **Widget** → `com.work.xux.want.presentation.widget`

### Q: 如何處理複雜的組件？

**建議**：
- 拆分為多個私有子組件
- 每個子組件負責單一職責
- 使用有意義的命名

## 相關文檔

- [Jetpack Compose 官方文檔](https://developer.android.com/jetpack/compose)
- [MVI 架構指南](https://developer.android.com/topic/architecture)
- [項目 Compose 組件範例](../../../app/src/main/java/com/work/compose/components/)

## 技術實現細節

此 skill 會：
1. 分析組件名稱判斷類型（Screen/Card/Widget）
2. 檢查是否已存在同名文件
3. 根據項目結構決定文件位置
4. 生成符合項目規範的程式碼
5. 添加必要的 import 和註釋
6. 創建多種 Preview 狀態

所有生成的程式碼都遵循項目的 Kotlin 編碼規範和 MVI 架構模式。
