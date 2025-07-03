package com.shawn.kubomi

import androidx.lifecycle.ViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

class MainViewModel : ViewModel() {

    private val _loginState = MutableStateFlow<String>("")
    val loginState: StateFlow<String> = _loginState

    fun login(email: String, password: String) {
        // 請在這裡補上 viewModelScope + loginApi 的邏輯
    }
}