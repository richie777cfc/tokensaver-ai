package com.example.demo.ui

import androidx.compose.runtime.Composable
import androidx.navigation.NavController

@Composable
fun HomeScreen(navController: NavController) {
    navController.navigate("profile/123")
    navController.navigate("settings")
}

@Composable
fun SettingsScreen() {
    val apiKey = BuildConfig.API_KEY
    val baseUrl = BuildConfig.BASE_URL
}
