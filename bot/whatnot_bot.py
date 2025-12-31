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
        time.sleep(2)

        try:
            # Wait for and click the email login option if present
            try:
                email_login_btn = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Email')]"))
                )
                email_login_btn.click()
                time.sleep(1)
            except TimeoutException:
                pass  # Email form might already be visible

            # Find and fill email field
            email_field = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email'], input[name='email'], input[placeholder*='email' i]"))
            )
            email_field.clear()
            email_field.send_keys(self.config.email)
            time.sleep(0.5)

            # Find and fill password field
            password_field = self.driver.find_element(
                By.CSS_SELECTOR, "input[type='password'], input[name='password']"
            )
            password_field.clear()
            password_field.send_keys(self.config.password)
            time.sleep(0.5)

            # Submit the form
            password_field.send_keys(Keys.RETURN)

            # Wait for successful login (redirect or user menu)
            time.sleep(3)
            self._verify_login()

        except Exception as e:
            self.log(f"Login error: {str(e)}")
            raise

    def login_with_google(self):
        """Log into Whatnot using Google OAuth."""
        self.log("Navigating to Whatnot login page...")
        self.driver.get(self.config.login_url)
        time.sleep(2)

        try:
            # Find and click Google login button
            google_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Google')]"))
            )
            google_btn.click()

            # Wait for user to complete Google login manually
            self.log("Please complete Google login in the browser window...")
            self.log("Waiting up to 120 seconds for login...")

            # Wait for redirect back to Whatnot
            for _ in range(120):
                time.sleep(1)
                if "whatnot.com" in self.driver.current_url and "login" not in self.driver.current_url:
                    break

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
