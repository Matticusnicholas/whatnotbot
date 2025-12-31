"""
Whatnot Giveaway Bot - Web Application
A Flask-based web app that automates entering giveaways on Whatnot streams.
"""

import os
import json
import threading
import time
from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit
from bot.whatnot_bot import WhatnotBot
from bot.config import BotConfig

app = Flask(__name__)
app.secret_key = os.urandom(24)
socketio = SocketIO(app, cors_allowed_origins="*")

# Global bot instance and state
bot_instance = None
bot_thread = None
bot_running = False
bot_status = {
    "state": "idle",
    "current_stream": None,
    "giveaways_entered": 0,
    "streams_visited": 0,
    "last_action": None,
    "logs": []
}


def add_log(message):
    """Add a log message and emit to clients."""
    timestamp = time.strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    bot_status["logs"].append(log_entry)
    # Keep only last 100 logs
    if len(bot_status["logs"]) > 100:
        bot_status["logs"] = bot_status["logs"][-100:]
    socketio.emit("log", {"message": log_entry})
    socketio.emit("status_update", bot_status)


@app.route("/")
def index():
    """Render the main page."""
    return render_template("index.html")


@app.route("/api/start", methods=["POST"])
def start_bot():
    """Start the bot with provided configuration."""
    global bot_instance, bot_thread, bot_running, bot_status

    if bot_running:
        return jsonify({"success": False, "error": "Bot is already running"})

    data = request.json

    # Create bot configuration
    config = BotConfig(
        browser=data.get("browser", "chrome"),
        login_method=data.get("login_method", "credentials"),
        email=data.get("email", ""),
        password=data.get("password", ""),
        headless=data.get("headless", False),
        use_profile=data.get("use_profile", False),
        giveaway_wait_time=data.get("giveaway_wait_time", 30),
        stream_check_interval=data.get("stream_check_interval", 5),
        max_streams=data.get("max_streams", 50)
    )

    try:
        bot_instance = WhatnotBot(config, status_callback=add_log)
        bot_running = True
        bot_status["state"] = "starting"
        bot_status["giveaways_entered"] = 0
        bot_status["streams_visited"] = 0
        bot_status["logs"] = []

        # Start bot in background thread
        bot_thread = threading.Thread(target=run_bot, args=(config,))
        bot_thread.daemon = True
        bot_thread.start()

        return jsonify({"success": True, "message": "Bot started successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


def run_bot(config):
    """Run the bot in a background thread."""
    global bot_instance, bot_running, bot_status

    try:
        add_log("Initializing browser...")
        bot_instance.initialize_browser()

        add_log("Logging into Whatnot...")
        bot_status["state"] = "logging_in"

        if config.login_method == "manual":
            add_log("Manual login mode - please log in using the browser window...")
            bot_instance.login_manual()
        elif config.login_method == "google":
            add_log("Please complete Google login in the browser window...")
            bot_instance.login_with_google()
        else:
            bot_instance.login_with_credentials()

        add_log("Login successful! Starting giveaway hunt...")
        bot_status["state"] = "hunting"

        # Main bot loop
        while bot_running:
            try:
                # Find streams with giveaways
                streams = bot_instance.find_giveaway_streams()

                for stream in streams:
                    if not bot_running:
                        break

                    bot_status["current_stream"] = stream.get("title", "Unknown")
                    bot_status["streams_visited"] += 1
                    add_log(f"Entering stream: {stream.get('title', 'Unknown')}")

                    bot_instance.enter_stream(stream)

                    # Check for and enter giveaways
                    while bot_running:
                        giveaway = bot_instance.detect_giveaway()

                        if giveaway:
                            add_log(f"Found giveaway: {giveaway.get('title', 'Giveaway')}")
                            success = bot_instance.enter_giveaway(giveaway)

                            if success:
                                bot_status["giveaways_entered"] += 1
                                add_log("Successfully entered giveaway!")

                            # Wait for giveaway to complete
                            add_log("Waiting for giveaway to complete...")
                            bot_instance.wait_for_giveaway_completion(config.giveaway_wait_time)

                            # Check for follow-up giveaway
                            add_log("Checking for follow-up giveaway...")
                            time.sleep(5)
                        else:
                            # No more giveaways, move to next stream
                            add_log("No active giveaway found, moving to next stream...")
                            break

                    time.sleep(2)

                # Wait before checking for more streams
                add_log("Refreshing stream list...")
                time.sleep(config.stream_check_interval)

            except Exception as e:
                add_log(f"Error during bot operation: {str(e)}")
                time.sleep(5)

    except Exception as e:
        add_log(f"Bot error: {str(e)}")
        bot_status["state"] = "error"
    finally:
        if bot_instance:
            bot_instance.cleanup()
        bot_status["state"] = "stopped"
        add_log("Bot stopped")


@app.route("/api/stop", methods=["POST"])
def stop_bot():
    """Stop the running bot."""
    global bot_running, bot_status

    if not bot_running:
        return jsonify({"success": False, "error": "Bot is not running"})

    bot_running = False
    bot_status["state"] = "stopping"
    add_log("Stopping bot...")

    return jsonify({"success": True, "message": "Bot stop requested"})


@app.route("/api/status", methods=["GET"])
def get_status():
    """Get current bot status."""
    return jsonify(bot_status)


@socketio.on("connect")
def handle_connect():
    """Handle client connection."""
    emit("status_update", bot_status)


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
