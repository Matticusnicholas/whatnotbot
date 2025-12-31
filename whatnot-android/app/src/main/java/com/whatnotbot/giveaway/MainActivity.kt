package com.whatnotbot.giveaway

import android.accessibilityservice.AccessibilityServiceInfo
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.view.View
import android.view.accessibility.AccessibilityManager
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat

class MainActivity : AppCompatActivity() {

    private lateinit var btnAccessibility: Button
    private lateinit var btnOverlay: Button
    private lateinit var btnStartStop: Button
    private lateinit var statusText: TextView
    private lateinit var giveawayCount: TextView
    private lateinit var accessibilityIndicator: View
    private lateinit var overlayIndicator: View

    private var isServiceRunning = false

    companion object {
        const val PREFS_NAME = "WhatnotBotPrefs"
        const val KEY_GIVEAWAY_COUNT = "giveaway_count"

        // Shared state for the service
        var giveawaysEntered = 0
        var isBotActive = false
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        initViews()
        setupClickListeners()
        loadStats()
    }

    override fun onResume() {
        super.onResume()
        updatePermissionStatus()
        updateServiceStatus()
    }

    private fun initViews() {
        btnAccessibility = findViewById(R.id.btnAccessibility)
        btnOverlay = findViewById(R.id.btnOverlay)
        btnStartStop = findViewById(R.id.btnStartStop)
        statusText = findViewById(R.id.statusText)
        giveawayCount = findViewById(R.id.giveawayCount)
        accessibilityIndicator = findViewById(R.id.accessibilityIndicator)
        overlayIndicator = findViewById(R.id.overlayIndicator)
    }

    private fun setupClickListeners() {
        btnAccessibility.setOnClickListener {
            openAccessibilitySettings()
        }

        btnOverlay.setOnClickListener {
            openOverlaySettings()
        }

        btnStartStop.setOnClickListener {
            toggleService()
        }
    }

    private fun loadStats() {
        val prefs = getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        giveawaysEntered = prefs.getInt(KEY_GIVEAWAY_COUNT, 0)
        updateGiveawayCount()
    }

    private fun updateGiveawayCount() {
        giveawayCount.text = "Giveaways Entered: $giveawaysEntered"
    }

    private fun updatePermissionStatus() {
        val accessibilityEnabled = isAccessibilityServiceEnabled()
        val overlayEnabled = Settings.canDrawOverlays(this)

        // Update indicators
        val greenColor = ContextCompat.getColor(this, R.color.success_green)
        val redColor = ContextCompat.getColor(this, R.color.whatnot_primary)

        accessibilityIndicator.setBackgroundColor(if (accessibilityEnabled) greenColor else redColor)
        overlayIndicator.setBackgroundColor(if (overlayEnabled) greenColor else redColor)

        // Update button text
        btnAccessibility.text = if (accessibilityEnabled) "Enabled" else "Enable"
        btnOverlay.text = if (overlayEnabled) "Enabled" else "Enable"

        // Enable/disable start button
        btnStartStop.isEnabled = accessibilityEnabled && overlayEnabled
        btnStartStop.alpha = if (btnStartStop.isEnabled) 1.0f else 0.5f
    }

    private fun updateServiceStatus() {
        if (isBotActive) {
            statusText.text = "Status: Running"
            statusText.setTextColor(ContextCompat.getColor(this, R.color.success_green))
            btnStartStop.text = getString(R.string.stop_bot)
            btnStartStop.setBackgroundColor(ContextCompat.getColor(this, R.color.whatnot_primary))
        } else {
            statusText.text = "Status: Idle"
            statusText.setTextColor(ContextCompat.getColor(this, R.color.white))
            btnStartStop.text = getString(R.string.start_bot)
            btnStartStop.setBackgroundColor(ContextCompat.getColor(this, R.color.success_green))
        }
        updateGiveawayCount()
    }

    private fun isAccessibilityServiceEnabled(): Boolean {
        val am = getSystemService(Context.ACCESSIBILITY_SERVICE) as AccessibilityManager
        val enabledServices = am.getEnabledAccessibilityServiceList(AccessibilityServiceInfo.FEEDBACK_ALL_MASK)

        for (service in enabledServices) {
            if (service.id.contains(packageName)) {
                return true
            }
        }
        return false
    }

    private fun openAccessibilitySettings() {
        val intent = Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)
        startActivity(intent)
    }

    private fun openOverlaySettings() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            val intent = Intent(
                Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                Uri.parse("package:$packageName")
            )
            startActivity(intent)
        }
    }

    private fun toggleService() {
        if (isBotActive) {
            stopOverlayService()
        } else {
            startOverlayService()
        }
        updateServiceStatus()
    }

    private fun startOverlayService() {
        isBotActive = true
        val intent = Intent(this, OverlayService::class.java)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(intent)
        } else {
            startService(intent)
        }
    }

    private fun stopOverlayService() {
        isBotActive = false
        val intent = Intent(this, OverlayService::class.java)
        stopService(intent)
    }

    fun incrementGiveawayCount() {
        giveawaysEntered++
        val prefs = getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        prefs.edit().putInt(KEY_GIVEAWAY_COUNT, giveawaysEntered).apply()
        runOnUiThread { updateGiveawayCount() }
    }
}
