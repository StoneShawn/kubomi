package com.shawn.kubomi.train

import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking


fun main() = runBlocking {
    println("--- 協程 (Coroutines) 與執行緒 (Threads) 範例 ---")
    println("當前執行緒: ${Thread.currentThread().name}") // 通常是 main 執行緒

    // 範例 1: 啟動一個簡單的協程
    println("\n--- 範例 1: 啟動一個簡單的協程 ---")
    // launch 是一個協程構建器，它啟動一個新的協程，不阻塞當前執行緒
    val job1 = launch {
        println("協程 1: 啟動中...")
        delay(1000L) // suspend 函數，非阻塞式延遲 1 秒
        println("協程 1: 完成。執行緒: ${Thread.currentThread().name}")
    }
    println("主函數: 協程 1 已啟動，繼續執行...")
    job1.join() // 等待協程 1 完成，這裡為了演示同步等待效果，實際應用中通常不需要立即 join
    println("主函數: 協程 1 已結束。")
    println()
}