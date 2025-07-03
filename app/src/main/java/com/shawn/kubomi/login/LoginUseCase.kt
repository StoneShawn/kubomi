package com.shawn.kubomi.login

class LoginUseCase(val loginRepository: loginRepository) {
    suspend fun invoke(account: String, password: String): String{
        return loginRepository.login(account, password)
    }
}