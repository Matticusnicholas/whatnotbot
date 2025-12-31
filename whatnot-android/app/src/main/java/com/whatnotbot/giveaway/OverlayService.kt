package com.whatnotbot.giveaway

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.graphics.Color
import android.graphics.PixelFormat
import android.graphics.drawable.GradientDrawable
import android.os.Build
import android.os.IBinder
import android.util.Log
import android.view.Gravity
import android.view.LayoutInflater
import android.view.MotionEvent
import android.view.View
import android.view.WindowManager
import android.widget.ImageView
import android.widget.Toast
import androidx.core.app.NotificationCompat

class OverlayService : Service() {

    companion object {
        private const val TAG = "OverlayService"
        private const val CHANNEL_ID = "WhatnotBotChannel"
        private const val NOTIFICATION_ID = 1001

        var instance: OverlayService? = null
            private set
    }

    private lateinit var windowManager: WindowManager
    private var overlayView: View? = null
    private var statusDot: View? = null
    private var overlayButton: ImageView? = null

    private var initialX = 0
    private var initialY = 0
    private var initialTouchX = 0f
    private var initialTouchY = 0f

    override fun onCreate() {
        super.onCreate()
        instance = this
        windowManager = getSystemService(Context.WINDOW_SERVICE) as WindowManager
        createNotificationChannel()
        startForeground(NOTIFICATION_ID, createNotification())
        createOverlay()
        startAccessibilityScanning()
        Log.d(TAG, "Overlay Service created")
    }

    override fun onDestroy() {
        super.onDestroy()
        instance = null
        removeOverlay()
        stopAccessibilityScanning()
        Log.d(TAG, "Overlay Service destroyed")
    }

    override fun onBind(intent: Intent?): IBinder? = null

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                getString(R.string.notification_channel_name),
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Whatnot Giveaway Bot is running"
                setShowBadge(false)
            }

            val notificationManager = getSystemService(NotificationManager::class.java)
            notificationManager.createNotificationChannel(channel)
        }
    }

    private fun createNotification(): Notification {
        val intent = Intent(this, MainActivity::class.java)
        val pendingIntent = PendingIntent.getActivity(
            this, 0, intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle(getString(R.string.notification_title))
            .setContentText(getString(R.string.notification_text))
            .setSmallIcon(R.drawable.ic_gift)
            .setContentIntent(pendingIntent)
            .setOngoing(true)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .build()
    }

    private fun createOverlay() {
        val inflater = getSystemService(Context.LAYOUT_INFLATER_SERVICE) as LayoutInflater
        overlayView = inflater.inflate(R.layout.overlay_layout, null)

        overlayButton = overlayView?.findViewById(R.id.overlayButton)
        statusDot = overlayView?.findViewById(R.id.statusDot)

        val layoutFlag = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY
        } else {
            @Suppress("DEPRECATION")
            WindowManager.LayoutParams.TYPE_PHONE
        }

        val params = WindowManager.LayoutParams(
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.WRAP_CONTENT,
            layoutFlag,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
            PixelFormat.TRANSLUCENT
        ).apply {
            gravity = Gravity.TOP or Gravity.START
            x = 20
            y = 200
        }

        // Set up touch listener for dragging
        overlayView?.setOnTouchListener { view, event ->
            when (event.action) {
                MotionEvent.ACTION_DOWN -> {
                    initialX = params.x
                    initialY = params.y
                    initialTouchX = event.rawX
                    initialTouchY = event.rawY
                    true
                }
                MotionEvent.ACTION_MOVE -> {
                    params.x = initialX + (event.rawX - initialTouchX).toInt()
                    params.y = initialY + (event.rawY - initialTouchY).toInt()
                    windowManager.updateViewLayout(overlayView, params)
                    true
                }
                MotionEvent.ACTION_UP -> {
                    val deltaX = event.rawX - initialTouchX
                    val deltaY = event.rawY - initialTouchY
                    // If minimal movement, treat as click
                    if (Math.abs(deltaX) < 10 && Math.abs(deltaY) < 10) {
                        toggleBot()
                    }
                    true
                }
                else -> false
            }
        }

        try {
            windowManager.addView(overlayView, params)
            updateStatusDot(true)
            Log.d(TAG, "Overlay created")
        } catch (e: Exception) {
            Log.e(TAG, "Error creating overlay: ${e.message}")
        }
    }

    private fun removeOverlay() {
        try {
            if (overlayView != null) {
                windowManager.removeView(overlayView)
                overlayView = null
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error removing overlay: ${e.message}")
        }
    }

    private fun toggleBot() {
        MainActivity.isBotActive = !MainActivity.isBotActive

        if (MainActivity.isBotActive) {
            startAccessibilityScanning()
            updateStatusDot(true)
            Toast.makeText(this, "Bot Active - Watching for giveaways", Toast.LENGTH_SHORT).show()
        } else {
            stopAccessibilityScanning()
            updateStatusDot(false)
            Toast.makeText(this, "Bot Paused", Toast.LENGTH_SHORT).show()
        }
    }

    private fun startAccessibilityScanning() {
        GiveawayAccessibilityService.instance?.startScanning()
    }

    private fun stopAccessibilityScanning() {
        GiveawayAccessibilityService.instance?.stopScanning()
    }

    private fun updateStatusDot(active: Boolean) {
        statusDot?.let { dot ->
            val drawable = GradientDrawable().apply {
                shape = GradientDrawable.OVAL
                setColor(if (active) Color.parseColor("#28A745") else Color.parseColor("#DC3545"))
                setStroke(2, Color.WHITE)
            }
            dot.background = drawable
        }
    }

    fun updateStatus(message: String) {
        // Flash the status dot to indicate action
        updateStatusDot(true)
        Log.d(TAG, "Status: $message")
    }
}
