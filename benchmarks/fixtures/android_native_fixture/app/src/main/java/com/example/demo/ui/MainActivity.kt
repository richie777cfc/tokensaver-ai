package com.example.demo.ui

import android.content.Intent
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            val navController = rememberNavController()
            NavHost(navController, startDestination = "home") {
                composable("home") { HomeScreen(navController) }
                composable("profile/{userId}") { ProfileScreen(it) }
                composable("settings") { SettingsScreen() }
            }
        }
    }

    private fun openDetail() {
        val intent = Intent(this, DetailActivity::class.java)
        startActivity(intent)
    }
}

class DetailActivity : ComponentActivity()
