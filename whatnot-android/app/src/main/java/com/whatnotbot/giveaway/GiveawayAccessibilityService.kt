package com.whatnotbot.giveaway

import android.accessibilityservice.AccessibilityService
import android.accessibilityservice.GestureDescription
import android.content.Context
import android.graphics.Path
import android.graphics.Rect
import android.os.Build
import android.os.Handler
import android.os.Looper
import android.util.Log
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo

class GiveawayAccessibilityService : AccessibilityService() {

    companion object {
        private const val TAG = "GiveawayBot"
        private const val WHATNOT_PACKAGE = "com.whatnot.whatnot"

        // Timing constants
        private const val SCAN_INTERVAL_MS = 1000L  // Check every second
        private const val TAP_DELAY_MS = 500L       // Delay between taps
        private const val COOLDOWN_MS = 3000L       // Cooldown after entering

        // Singleton instance for overlay to communicate
        var instance: GiveawayAccessibilityService? = null
            private set
    }

    private val handler = Handler(Looper.getMainLooper())
    private var isScanning = false
    private var lastActionTime = 0L
    private var currentState = BotState.IDLE

    enum class BotState {
        IDLE,           // Not doing anything
        WATCHING,       // Watching for giveaway button
        ENTERING,       // In process of entering
        ENTERED,        // Successfully entered, waiting
        COOLDOWN        // Just entered, waiting before next action
    }

    private val scanRunnable = object : Runnable {
        override fun run() {
            if (MainActivity.isBotActive && isWhatnotApp()) {
                scanForGiveaway()
            }
            if (isScanning) {
                handler.postDelayed(this, SCAN_INTERVAL_MS)
            }
        }
    }

    override fun onCreate() {
        super.onCreate()
        instance = this
        Log.d(TAG, "Accessibility Service created")
    }

    override fun onDestroy() {
        super.onDestroy()
        instance = null
        stopScanning()
        Log.d(TAG, "Accessibility Service destroyed")
    }

    override fun onServiceConnected() {
        super.onServiceConnected()
        Log.d(TAG, "Accessibility Service connected")
        startScanning()
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        // We handle scanning in our runnable, but we can also respond to events
        if (event == null) return

        // Only process if bot is active and we're in Whatnot
        if (!MainActivity.isBotActive) return
        if (event.packageName != WHATNOT_PACKAGE) return

        when (event.eventType) {
            AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED,
            AccessibilityEvent.TYPE_WINDOW_CONTENT_CHANGED -> {
                // Screen changed, might want to scan
                if (currentState == BotState.WATCHING) {
                    handler.removeCallbacks(scanRunnable)
                    handler.postDelayed(scanRunnable, 200)
                }
            }
        }
    }

    override fun onInterrupt() {
        Log.d(TAG, "Accessibility Service interrupted")
    }

    fun startScanning() {
        if (!isScanning) {
            isScanning = true
            currentState = BotState.WATCHING
            handler.post(scanRunnable)
            Log.d(TAG, "Started scanning for giveaways")
        }
    }

    fun stopScanning() {
        isScanning = false
        currentState = BotState.IDLE
        handler.removeCallbacks(scanRunnable)
        Log.d(TAG, "Stopped scanning")
    }

    private fun isWhatnotApp(): Boolean {
        val rootNode = rootInActiveWindow ?: return false
        return rootNode.packageName == WHATNOT_PACKAGE
    }

    private fun scanForGiveaway() {
        if (!MainActivity.isBotActive) return

        val rootNode = rootInActiveWindow ?: return

        try {
            when (currentState) {
                BotState.WATCHING, BotState.IDLE -> {
                    // Look for giveaway indicators
                    if (findAndTapGiveawayButton(rootNode)) {
                        currentState = BotState.ENTERING
                    } else if (findEnterGiveawayButton(rootNode)) {
                        // Card is already expanded, tap enter
                        currentState = BotState.ENTERING
                    } else if (isAlreadyEntered(rootNode)) {
                        currentState = BotState.ENTERED
                        Log.d(TAG, "Already in giveaway, watching for next one")
                    }
                }
                BotState.ENTERING -> {
                    // Tap the enter button
                    if (tapEnterButton(rootNode)) {
                        currentState = BotState.COOLDOWN
                        incrementGiveawayCount()
                        handler.postDelayed({
                            currentState = BotState.WATCHING
                        }, COOLDOWN_MS)
                    }
                }
                BotState.ENTERED -> {
                    // Check if giveaway ended or new one started
                    if (!isAlreadyEntered(rootNode)) {
                        currentState = BotState.WATCHING
                    }
                }
                BotState.COOLDOWN -> {
                    // Wait for cooldown
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error scanning: ${e.message}")
        } finally {
            rootNode.recycle()
        }
    }

    private fun findAndTapGiveawayButton(rootNode: AccessibilityNodeInfo): Boolean {
        // Look for the "Giveaway" badge with entries count (top right area)
        // It typically shows "Giveaway" and "X Entries"

        val giveawayNodes = mutableListOf<AccessibilityNodeInfo>()

        // Search for text containing "Giveaway"
        findNodesByText(rootNode, "Giveaway", giveawayNodes)
        findNodesByText(rootNode, "giveaway", giveawayNodes)

        for (node in giveawayNodes) {
            // Check if this is the badge (not the expanded card)
            val bounds = Rect()
            node.getBoundsInScreen(bounds)

            // Badge is typically in top right area (x > half screen width, y < 300)
            val screenWidth = resources.displayMetrics.widthPixels
            if (bounds.left > screenWidth / 2 && bounds.top < 400) {
                // This looks like the giveaway badge, tap it
                Log.d(TAG, "Found giveaway badge at: $bounds")

                if (performTap(bounds.centerX(), bounds.centerY())) {
                    Log.d(TAG, "Tapped giveaway badge")
                    return true
                }
            }
        }

        return false
    }

    private fun findEnterGiveawayButton(rootNode: AccessibilityNodeInfo): Boolean {
        // Look for "Enter Giveaway" button text
        val enterNodes = mutableListOf<AccessibilityNodeInfo>()
        findNodesByText(rootNode, "Enter Giveaway", enterNodes)
        findNodesByText(rootNode, "Follow and Enter", enterNodes)

        return enterNodes.isNotEmpty()
    }

    private fun tapEnterButton(rootNode: AccessibilityNodeInfo): Boolean {
        // Find and tap "Enter Giveaway" or "Follow and Enter" button
        val buttonTexts = listOf("Enter Giveaway", "Follow and Enter", "Enter")

        for (buttonText in buttonTexts) {
            val nodes = mutableListOf<AccessibilityNodeInfo>()
            findNodesByText(rootNode, buttonText, nodes)

            for (node in nodes) {
                if (node.isClickable || node.isEnabled) {
                    val bounds = Rect()
                    node.getBoundsInScreen(bounds)

                    // Make sure it's in a reasonable position (top area where card appears)
                    if (bounds.top < 600) {
                        Log.d(TAG, "Found enter button: $buttonText at $bounds")

                        if (performTap(bounds.centerX(), bounds.centerY())) {
                            Log.d(TAG, "Tapped enter button!")
                            return true
                        }
                    }
                }
            }
        }

        return false
    }

    private fun isAlreadyEntered(rootNode: AccessibilityNodeInfo): Boolean {
        // Look for "You're in the Giveaway" text
        val enteredNodes = mutableListOf<AccessibilityNodeInfo>()
        findNodesByText(rootNode, "You're in the Giveaway", enteredNodes)
        findNodesByText(rootNode, "You're in", enteredNodes)

        return enteredNodes.isNotEmpty()
    }

    private fun findNodesByText(
        node: AccessibilityNodeInfo,
        text: String,
        results: MutableList<AccessibilityNodeInfo>
    ) {
        // Check current node
        val nodeText = node.text?.toString() ?: ""
        val contentDesc = node.contentDescription?.toString() ?: ""

        if (nodeText.contains(text, ignoreCase = true) ||
            contentDesc.contains(text, ignoreCase = true)) {
            results.add(node)
        }

        // Check children
        for (i in 0 until node.childCount) {
            val child = node.getChild(i) ?: continue
            findNodesByText(child, text, results)
        }
    }

    private fun performTap(x: Int, y: Int): Boolean {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.N) {
            return false
        }

        val now = System.currentTimeMillis()
        if (now - lastActionTime < TAP_DELAY_MS) {
            return false // Too soon after last tap
        }

        val path = Path()
        path.moveTo(x.toFloat(), y.toFloat())

        val gesture = GestureDescription.Builder()
            .addStroke(GestureDescription.StrokeDescription(path, 0, 100))
            .build()

        val result = dispatchGesture(gesture, object : GestureResultCallback() {
            override fun onCompleted(gestureDescription: GestureDescription?) {
                Log.d(TAG, "Tap completed at ($x, $y)")
            }

            override fun onCancelled(gestureDescription: GestureDescription?) {
                Log.d(TAG, "Tap cancelled")
            }
        }, null)

        if (result) {
            lastActionTime = now
        }

        return result
    }

    private fun incrementGiveawayCount() {
        MainActivity.giveawaysEntered++
        val prefs = getSharedPreferences(MainActivity.PREFS_NAME, Context.MODE_PRIVATE)
        prefs.edit().putInt(MainActivity.KEY_GIVEAWAY_COUNT, MainActivity.giveawaysEntered).apply()
        Log.d(TAG, "Giveaway entered! Total: ${MainActivity.giveawaysEntered}")

        // Notify overlay to update
        OverlayService.instance?.updateStatus("Entered! Total: ${MainActivity.giveawaysEntered}")
    }

    fun getCurrentState(): BotState = currentState
}
