"""
Whatnot Bot - Selenium-based automation for Whatnot giveaways.
"""

import time
import re
from typing import Optional, Callable, List, Dict, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.safari.options import Options as SafariOptions
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,
    StaleElementReferenceException
)
from webdriver_manager.firefox import GeckoDriverManager

from .config import BotConfig


class WhatnotBot:
    """Automated bot for entering Whatnot giveaways."""

    def __init__(self, config: BotConfig, status_callback: Optional[Callable] = None):
        """
        Initialize the bot with configuration.

        Args:
            config: Bot configuration object
            status_callback: Optional callback function for status updates
        """
        self.config = config
        self.driver: Optional[webdriver.Remote] = None
        self.wait: Optional[WebDriverWait] = None
        self.status_callback = status_callback or print
        self.logged_in = False
        self.visited_streams = set()

    def log(self, message: str):
        """Log a message using the status callback."""
        self.status_callback(message)

    def initialize_browser(self):
        """Initialize the Selenium WebDriver based on configuration."""
        self.log(f"Initializing {self.config.browser} browser...")

        if self.config.browser == "firefox":
            options = FirefoxOptions()
            if self.config.headless:
                options.add_argument("--headless")

            # Common Firefox settings
            options.set_preference("dom.webnotifications.enabled", False)
            options.set_preference("media.volume_scale", "0.0")

            try:
                # Try to use webdriver-manager for automatic driver management
                service = FirefoxService(GeckoDriverManager().install())
                self.driver = webdriver.Firefox(service=service, options=options)
            except Exception:
                # Fallback to system geckodriver
                self.driver = webdriver.Firefox(options=options)

        elif self.config.browser == "safari":
            # Safari WebDriver (macOS only)
            options = SafariOptions()
            self.driver = webdriver.Safari(options=options)

        else:
            raise ValueError(f"Unsupported browser: {self.config.browser}")

        # Set up wait
        self.wait = WebDriverWait(self.driver, 10)
        self.driver.maximize_window()
        self.log("Browser initialized successfully")

    def login_with_credentials(self):
        """Log into Whatnot using email and password."""
        self.log("Navigating to Whatnot login page...")
        self.driver.get(self.config.login_url)
        time.sleep(3)

        try:
            # Log page info for debugging
            self.log(f"Current URL: {self.driver.current_url}")

            # First, try to find and click "Log in with Email" or similar button
            email_login_buttons = [
                "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'email')]",
                "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'log in')]",
                "//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'email')]",
                "//div[contains(@class, 'email')]//button",
                "//span[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'email')]/ancestor::button",
            ]

            for xpath in email_login_buttons:
                try:
                    buttons = self.driver.find_elements(By.XPATH, xpath)
                    for btn in buttons:
                        if btn.is_displayed():
                            self.log(f"Found email login button: {btn.text}")
                            btn.click()
                            time.sleep(2)
                            break
                except Exception:
                    continue

            # Wait for page to settle
            time.sleep(2)

            # Find all input fields and log them for debugging
            all_inputs = self.driver.find_elements(By.TAG_NAME, "input")
            self.log(f"Found {len(all_inputs)} input fields on page")

            for idx, inp in enumerate(all_inputs):
                inp_type = inp.get_attribute("type")
                inp_name = inp.get_attribute("name")
                inp_placeholder = inp.get_attribute("placeholder")
                inp_id = inp.get_attribute("id")
                self.log(f"Input {idx}: type={inp_type}, name={inp_name}, placeholder={inp_placeholder}, id={inp_id}")

            # Try multiple strategies to find email field
            email_field = None
            email_selectors = [
                (By.CSS_SELECTOR, "input[type='email']"),
                (By.CSS_SELECTOR, "input[name='email']"),
                (By.CSS_SELECTOR, "input[name='username']"),
                (By.CSS_SELECTOR, "input[placeholder*='email' i]"),
                (By.CSS_SELECTOR, "input[placeholder*='Email']"),
                (By.CSS_SELECTOR, "input[autocomplete='email']"),
                (By.CSS_SELECTOR, "input[autocomplete='username']"),
                (By.XPATH, "//input[@type='text' or @type='email'][1]"),
                (By.XPATH, "//label[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'email')]/following::input[1]"),
                (By.XPATH, "//label[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'email')]/..//input"),
            ]

            for by, selector in email_selectors:
                try:
                    elements = self.driver.find_elements(by, selector)
                    for el in elements:
                        if el.is_displayed() and el.is_enabled():
                            email_field = el
                            self.log(f"Found email field with selector: {selector}")
                            break
                    if email_field:
                        break
                except Exception:
                    continue

            if not email_field:
                # Fallback: use first visible text input
                for inp in all_inputs:
                    if inp.is_displayed() and inp.get_attribute("type") in ["text", "email", ""]:
                        email_field = inp
                        self.log("Using first visible text input as email field")
                        break

            if not email_field:
                raise Exception("Could not find email input field")

            # Clear and fill email
            self.log("Entering email...")
            email_field.click()
            time.sleep(0.3)
            email_field.clear()
            time.sleep(0.2)

            # Type email character by character for reliability
            for char in self.config.email:
                email_field.send_keys(char)
                time.sleep(0.05)

            time.sleep(0.5)

            # Find password field
            password_field = None
            password_selectors = [
                (By.CSS_SELECTOR, "input[type='password']"),
                (By.CSS_SELECTOR, "input[name='password']"),
                (By.CSS_SELECTOR, "input[autocomplete='current-password']"),
                (By.XPATH, "//input[@type='password']"),
                (By.XPATH, "//label[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'password')]/following::input[1]"),
            ]

            for by, selector in password_selectors:
                try:
                    elements = self.driver.find_elements(by, selector)
                    for el in elements:
                        if el.is_displayed() and el.is_enabled():
                            password_field = el
                            self.log(f"Found password field with selector: {selector}")
                            break
                    if password_field:
                        break
                except Exception:
                    continue

            if not password_field:
                raise Exception("Could not find password input field")

            # Clear and fill password
            self.log("Entering password...")
            password_field.click()
            time.sleep(0.3)
            password_field.clear()
            time.sleep(0.2)

            # Type password character by character
            for char in self.config.password:
                password_field.send_keys(char)
                time.sleep(0.05)

            time.sleep(0.5)

            # Find and click submit button
            self.log("Looking for login button...")
            submit_button = None
            submit_selectors = [
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'log in')]"),
                (By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'login')]"),
                (By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'sign in')]"),
                (By.XPATH, "//input[@type='submit']"),
                (By.CSS_SELECTOR, "form button"),
            ]

            for by, selector in submit_selectors:
                try:
                    elements = self.driver.find_elements(by, selector)
                    for el in elements:
                        if el.is_displayed() and el.is_enabled():
                            submit_button = el
                            self.log(f"Found submit button: {el.text}")
                            break
                    if submit_button:
                        break
                except Exception:
                    continue

            if submit_button:
                submit_button.click()
                self.log("Clicked login button")
            else:
                # Fallback: press Enter on password field
                self.log("No submit button found, pressing Enter...")
                password_field.send_keys(Keys.RETURN)

            # Wait for login to complete
            self.log("Waiting for login to complete...")
            time.sleep(5)
            self._verify_login()

        except Exception as e:
            self.log(f"Login error: {str(e)}")
            # Try to save screenshot for debugging
            try:
                self.driver.save_screenshot("/tmp/whatnot_login_error.png")
                self.log("Screenshot saved to /tmp/whatnot_login_error.png")
            except Exception:
                pass
            raise

    def login_with_google(self):
        """Log into Whatnot using Google OAuth."""
        self.log("Navigating to Whatnot login page...")
        self.driver.get(self.config.login_url)
        time.sleep(3)

        try:
            # Find and click Google login button
            google_selectors = [
                "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'google')]",
                "//button[contains(@class, 'google')]",
                "//div[contains(@class, 'google')]//button",
                "//button[.//img[contains(@src, 'google')]]",
                "//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'google')]",
            ]

            google_btn = None
            for xpath in google_selectors:
                try:
                    buttons = self.driver.find_elements(By.XPATH, xpath)
                    for btn in buttons:
                        if btn.is_displayed():
                            google_btn = btn
                            break
                    if google_btn:
                        break
                except Exception:
                    continue

            if google_btn:
                self.log("Found Google login button, clicking...")
                google_btn.click()
            else:
                self.log("Could not find Google button automatically.")
                self.log("Please click 'Continue with Google' manually in the browser.")

            # Wait for user to complete Google login manually
            self.log("Please complete Google login in the browser window...")
            self.log("Waiting up to 180 seconds for login...")

            # Wait for redirect back to Whatnot
            for i in range(180):
                time.sleep(1)
                current_url = self.driver.current_url
                if "whatnot.com" in current_url and "login" not in current_url and "auth" not in current_url:
                    self.log("Detected redirect back to Whatnot!")
                    break
                if i % 30 == 0 and i > 0:
                    self.log(f"Still waiting... ({180 - i} seconds remaining)")

            time.sleep(2)
            self._verify_login()

        except Exception as e:
            self.log(f"Google login error: {str(e)}")
            raise

    def _verify_login(self):
        """Verify that login was successful."""
        time.sleep(2)

        # Check if we're still on login page
        if "login" in self.driver.current_url.lower():
            # Check for error messages
            try:
                error = self.driver.find_element(By.CSS_SELECTOR, "[class*='error'], [class*='Error']")
                raise Exception(f"Login failed: {error.text}")
            except NoSuchElementException:
                raise Exception("Login appears to have failed")

        self.logged_in = True
        self.log("Login verified successfully")

    def find_giveaway_streams(self) -> List[Dict[str, Any]]:
        """Find live streams that may have giveaways."""
        self.log("Searching for live streams with giveaways...")
        streams = []

        try:
            # Navigate to live streams page
            self.driver.get(self.config.browse_url)
            time.sleep(3)

            # Scroll to load more streams
            for _ in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)

            # Find stream cards/tiles
            stream_elements = self.driver.find_elements(
                By.CSS_SELECTOR, "[data-testid='stream-card'], [class*='StreamCard'], [class*='stream-card'], a[href*='/live/']"
            )

            for element in stream_elements[:self.config.max_streams]:
                try:
                    # Get stream info
                    stream_url = element.get_attribute("href")
                    if not stream_url or stream_url in self.visited_streams:
                        continue

                    # Try to get title/text
                    title = element.text or "Unknown Stream"

                    # Look for giveaway indicators in the title/description
                    giveaway_keywords = ["giveaway", "giveaways", "free", "giving away", "raffle"]
                    title_lower = title.lower()

                    # Prioritize streams with giveaway keywords
                    has_giveaway_hint = any(kw in title_lower for kw in giveaway_keywords)

                    streams.append({
                        "url": stream_url,
                        "title": title[:50],
                        "element": element,
                        "priority": 1 if has_giveaway_hint else 0
                    })

                except StaleElementReferenceException:
                    continue

            # Sort by priority (giveaway hints first)
            streams.sort(key=lambda x: x["priority"], reverse=True)
            self.log(f"Found {len(streams)} live streams")

        except Exception as e:
            self.log(f"Error finding streams: {str(e)}")

        return streams

    def enter_stream(self, stream: Dict[str, Any]):
        """Navigate to and enter a stream."""
        try:
            stream_url = stream.get("url")
            if stream_url:
                self.driver.get(stream_url)
                self.visited_streams.add(stream_url)
                time.sleep(3)
            else:
                # Click the element directly
                element = stream.get("element")
                if element:
                    element.click()
                    time.sleep(3)

            self.log(f"Entered stream: {stream.get('title', 'Unknown')}")

        except Exception as e:
            self.log(f"Error entering stream: {str(e)}")

    def detect_giveaway(self) -> Optional[Dict[str, Any]]:
        """Detect if there's an active giveaway in the current stream."""
        try:
            # Common giveaway button/element selectors for Whatnot
            giveaway_selectors = [
                # Direct giveaway buttons
                "button[data-testid*='giveaway']",
                "button[class*='giveaway' i]",
                "button[class*='Giveaway']",
                "[data-testid='enter-giveaway-button']",
                "[class*='GiveawayEntry']",
                "[class*='giveaway-entry']",
                # Enter buttons that might be giveaways
                "button:contains('Enter')",
                "button[aria-label*='enter giveaway' i]",
                "button[aria-label*='Enter Giveaway']",
                # Modal or overlay giveaway elements
                "[class*='GiveawayModal']",
                "[class*='giveaway-modal']",
                "[role='dialog'] button[class*='enter' i]",
            ]

            # Also look for text-based indicators
            page_source = self.driver.page_source.lower()
            giveaway_active = any(indicator in page_source for indicator in [
                "enter giveaway", "giveaway entry", "free giveaway",
                "join giveaway", "click to enter"
            ])

            for selector in giveaway_selectors:
                try:
                    if ":contains" in selector:
                        # Use XPath for text-based selection
                        elements = self.driver.find_elements(
                            By.XPATH, "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'enter')]"
                        )
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)

                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            # Check if it looks like a giveaway button
                            text = element.text.lower()
                            if any(kw in text for kw in ["enter", "join", "giveaway", "free"]):
                                return {
                                    "element": element,
                                    "title": element.text or "Giveaway",
                                    "selector": selector
                                }
                except (NoSuchElementException, StaleElementReferenceException):
                    continue

            # Look for giveaway section in the page
            try:
                giveaway_sections = self.driver.find_elements(
                    By.XPATH, "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'giveaway')]"
                )
                for section in giveaway_sections:
                    # Find clickable button nearby
                    try:
                        button = section.find_element(By.XPATH, ".//button | ./following-sibling::button | ./ancestor::div//button")
                        if button.is_displayed() and button.is_enabled():
                            return {
                                "element": button,
                                "title": section.text[:30] if section.text else "Giveaway",
                                "selector": "giveaway-section"
                            }
                    except NoSuchElementException:
                        continue
            except Exception:
                pass

        except Exception as e:
            self.log(f"Error detecting giveaway: {str(e)}")

        return None

    def enter_giveaway(self, giveaway: Dict[str, Any]) -> bool:
        """Enter the detected giveaway."""
        try:
            element = giveaway.get("element")
            if not element:
                return False

            # Scroll element into view
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(0.5)

            # Try to click
            try:
                element.click()
            except ElementClickInterceptedException:
                # Try JavaScript click
                self.driver.execute_script("arguments[0].click();", element)

            self.log("Clicked giveaway entry button")
            time.sleep(1)

            # Check for confirmation or additional steps
            self._handle_giveaway_confirmation()

            return True

        except Exception as e:
            self.log(f"Error entering giveaway: {str(e)}")
            return False

    def _handle_giveaway_confirmation(self):
        """Handle any confirmation dialogs or additional entry steps."""
        try:
            # Look for confirm button
            confirm_selectors = [
                "button[data-testid*='confirm']",
                "button:contains('Confirm')",
                "button:contains('Yes')",
                "button:contains('Submit')",
                "[class*='confirm'] button",
            ]

            for selector in confirm_selectors:
                try:
                    if ":contains" in selector:
                        text = selector.split("'")[1]
                        buttons = self.driver.find_elements(
                            By.XPATH, f"//button[contains(text(), '{text}')]"
                        )
                    else:
                        buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)

                    for btn in buttons:
                        if btn.is_displayed() and btn.is_enabled():
                            btn.click()
                            self.log("Confirmed giveaway entry")
                            time.sleep(1)
                            return
                except Exception:
                    continue

        except Exception as e:
            self.log(f"Note: No confirmation needed or error: {str(e)}")

    def wait_for_giveaway_completion(self, timeout: int = 30):
        """Wait for the current giveaway to complete."""
        self.log(f"Waiting up to {timeout} seconds for giveaway completion...")

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Check for winner announcement
                winner_indicators = [
                    "[class*='winner' i]",
                    "[class*='Winner']",
                    "[data-testid*='winner']",
                    "*[contains(text(), 'Winner')]",
                    "*[contains(text(), 'Congratulations')]",
                ]

                for selector in winner_indicators:
                    try:
                        if "contains(text" in selector:
                            elements = self.driver.find_elements(
                                By.XPATH, f"//{selector}"
                            )
                        else:
                            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)

                        if elements:
                            self.log("Giveaway completed - winner announced")
                            return
                    except Exception:
                        continue

                # Check if giveaway entry button reappears (new giveaway)
                new_giveaway = self.detect_giveaway()
                if new_giveaway:
                    self.log("New giveaway detected!")
                    return

            except Exception:
                pass

            time.sleep(2)

        self.log("Giveaway wait timeout reached")

    def cleanup(self):
        """Clean up resources and close the browser."""
        if self.driver:
            try:
                self.driver.quit()
                self.log("Browser closed")
            except Exception as e:
                self.log(f"Error closing browser: {str(e)}")
