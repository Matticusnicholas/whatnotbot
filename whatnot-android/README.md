# Whatnot Giveaway Bot - Android App

An Android app that automatically enters giveaways while you watch Whatnot streams.

## How It Works

1. The app uses Android's Accessibility Service to read the Whatnot app screen
2. It watches for the "Giveaway" badge in the top right corner
3. When detected, it automatically taps to enter
4. A floating overlay button lets you control the bot

## Features

- **Auto-enter giveaways** - Detects and taps giveaway buttons automatically
- **Floating overlay** - Draggable button shows bot status
- **Stay on stream** - Keeps entering giveaways on current stream
- **Tap to pause** - Tap the floating button to pause/resume

## Installation

### Option 1: Build Online (No Android Studio Required)

1. Fork this repository to your GitHub account
2. Go to **Actions** tab in your forked repo
3. Click **Build APK** workflow
4. Click **Run workflow**
5. Wait for build to complete (~5 minutes)
6. Download the APK from **Artifacts**

### Option 2: Build Locally

```bash
cd whatnot-android
./gradlew assembleDebug
```

APK will be at: `app/build/outputs/apk/debug/app-debug.apk`

## Setup

1. **Install the APK** on your Android device
2. **Enable Accessibility Service**:
   - Open the app
   - Tap "Enable" next to Accessibility Service
   - Find "Whatnot Giveaway Bot" and enable it
3. **Enable Overlay Permission**:
   - Tap "Enable" next to Overlay Permission
   - Toggle on "Allow display over other apps"
4. **Start the Bot**:
   - Tap "Start Bot"
   - A floating gift icon appears

## Usage

1. Open the **Whatnot app**
2. Browse to a live stream
3. The bot will automatically:
   - Detect giveaway badges
   - Tap to open the giveaway card
   - Tap "Enter Giveaway" button
   - Wait for more giveaways on the same stream
4. **Tap the floating button** to pause/resume
5. **Drag the button** to reposition it

## Requirements

- Android 7.0 (API 24) or higher
- Whatnot app installed

## Disclaimer

Use at your own risk. This may violate Whatnot's Terms of Service.
