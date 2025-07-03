package com.shawn.kubomi.login

interface loginRepository {
    fun login(account: String , password: String): String
}