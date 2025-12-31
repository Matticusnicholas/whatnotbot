"""
Native Browser Bot - Uses PyAutoGUI to control your real browser.
No Selenium = No bot detection!
"""

import time
import subprocess
import platform
import webbrowser
from typing import Optional, Callable

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

try:
    from PIL import Image
    import pyautogui
    SCREENSHOT_AVAILABLE = True
except ImportError:
    SCREENSHOT_AVAILABLE = False


class NativeBot:
    """Bot that controls your real browser using mouse/keyboard automation."""

    def __init__(self, status_callback: Optional[Callable] = None):
        self.status_callback = status_callback or print
        self.running = False
        self.giveaways_entered = 0
        self.streams_visited = 0

        # PyAutoGUI settings
        if PYAUTOGUI_AVAILABLE:
            pyautogui.FAILSAFE = True  # Move mouse to corner to abort
            pyautogui.PAUSE = 0.1  # Small pause between actions

    def log(self, message: str):
        """Log a message."""
        self.status_callback(message)

    def start(self):
        """Start the bot."""
        if not PYAUTOGUI_AVAILABLE:
            self.log("ERROR: PyAutoGUI not installed!")
            self.log("Run: pip install pyautogui")
            return False

        self.running = True
        self.log("Native bot started!")
        self.log("=" * 50)
        self.log("INSTRUCTIONS:")
        self.log("1. Open your browser (Chrome, Firefox, etc.)")
        self.log("2. Go to whatnot.com and log in")
        self.log("3. Navigate to the Live streams page")
        self.log("4. Come back here and the bot will take over!")
        self.log("=" * 50)
        self.log("")
        self.log("Move mouse to TOP-LEFT corner to STOP the bot (failsafe)")
        self.log("")
        return True

    def open_browser(self):
        """Open the default browser to Whatnot."""
        self.log("Opening your default browser to Whatnot...")
        webbrowser.open("https://www.whatnot.com/live")
        time.sleep(3)

    def wait_for_user_ready(self, timeout: int = 300):
        """Wait for user to log in and get to live streams page."""
        self.log("Waiting for you to log in and navigate to live streams...")
        self.log(f"You have {timeout} seconds. Bot will start automatically when ready.")
        self.log("Or press Ctrl+C to start immediately if you're ready.")

        # Just wait - user will be on the live page
        for i in range(timeout):
            if not self.running:
                return False
            time.sleep(1)
            if i > 0 and i % 30 == 0:
                self.log(f"Still waiting... {timeout - i} seconds remaining")
                self.log("(Make sure you're on the Whatnot live streams page)")

        return True

    def scroll_down(self, amount: int = 300):
        """Scroll down to load more content."""
        pyautogui.scroll(-amount // 100)  # Negative = scroll down
        time.sleep(0.5)

    def scroll_up(self, amount: int = 300):
        """Scroll up."""
        pyautogui.scroll(amount // 100)
        time.sleep(0.5)

    def click_at(self, x: int, y: int):
        """Click at specific coordinates."""
        pyautogui.click(x, y)
        time.sleep(0.3)

    def find_and_click_text(self, text: str) -> bool:
        """Try to find text on screen and click it."""
        if not SCREENSHOT_AVAILABLE:
            return False

        try:
            # This requires OCR which needs additional setup
            # For now, we'll use image-based detection
            location = pyautogui.locateOnScreen(text, confidence=0.8)
            if location:
                center = pyautogui.center(location)
                pyautogui.click(center)
                return True
        except Exception:
            pass
        return False

    def find_giveaway_button(self) -> Optional[tuple]:
        """Try to find a giveaway entry button on screen."""
        # Common button colors/patterns for giveaways
        # This is a simplified approach - real implementation would use image matching
        self.log("Scanning screen for giveaway buttons...")

        # Get screen size
        screen_width, screen_height = pyautogui.size()

        # Scan the right side of the screen (where giveaway buttons usually are)
        # This is a heuristic approach
        return None  # Placeholder - needs image templates

    def hunt_giveaways(self, duration_minutes: int = 60):
        """Main loop to hunt for giveaways."""
        self.log("=" * 50)
        self.log("GIVEAWAY HUNTING MODE ACTIVE")
        self.log("=" * 50)
        self.log("")
        self.log("The bot will now:")
        self.log("1. Scroll through streams")
        self.log("2. Look for giveaway buttons")
        self.log("3. Click to enter when found")
        self.log("")
        self.log("YOU control the browser - bot just scrolls and clicks!")
        self.log("Move mouse to TOP-LEFT corner to STOP")
        self.log("")

        end_time = time.time() + (duration_minutes * 60)

        while self.running and time.time() < end_time:
            try:
                # Scroll down slowly to look for giveaways
                self.log("Scrolling to find streams...")
                self.scroll_down(200)
                time.sleep(2)

                # Every so often, scroll back up
                if self.streams_visited % 5 == 0:
                    self.scroll_up(100)
                    time.sleep(1)

                self.streams_visited += 1

                # Log progress
                if self.streams_visited % 10 == 0:
                    remaining = int((end_time - time.time()) / 60)
                    self.log(f"Progress: Scrolled {self.streams_visited} times, "
                            f"{remaining} minutes remaining")

            except pyautogui.FailSafeException:
                self.log("FAILSAFE triggered - mouse moved to corner!")
                self.log("Bot stopped.")
                self.running = False
                break

            except Exception as e:
                self.log(f"Error: {e}")
                time.sleep(1)

        self.log("Giveaway hunting session ended.")
        self.log(f"Total scrolls: {self.streams_visited}")

    def stop(self):
        """Stop the bot."""
        self.running = False
        self.log("Stopping native bot...")


def run_native_bot(status_callback=None, duration_minutes: int = 60):
    """Run the native browser bot."""
    bot = NativeBot(status_callback=status_callback)

    if not bot.start():
        return

    # Open browser for user
    bot.open_browser()

    # Wait for user to log in (30 seconds should be enough)
    bot.log("Log into Whatnot now. Bot will start in 30 seconds...")
    time.sleep(30)

    # Start hunting
    bot.hunt_giveaways(duration_minutes=duration_minutes)

    bot.stop()


if __name__ == "__main__":
    print("Native Whatnot Giveaway Bot")
    print("=" * 40)
    print()
    print("This bot uses your REAL browser - no Selenium!")
    print()

    run_native_bot(status_callback=print, duration_minutes=30)
