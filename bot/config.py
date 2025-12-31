"""Bot Configuration"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class BotConfig:
    """Configuration for the Whatnot bot."""

    # Browser settings
    browser: str = "chrome"  # "chrome" (recommended), "firefox", or "safari"
    headless: bool = False

    # Login settings
    login_method: str = "credentials"  # "credentials" or "google"
    email: str = ""
    password: str = ""

    # Bot behavior settings
    giveaway_wait_time: int = 30  # seconds to wait for giveaway completion
    stream_check_interval: int = 5  # seconds between stream refreshes
    max_streams: int = 50  # maximum streams to check per session

    # Whatnot URLs
    base_url: str = "https://www.whatnot.com"
    login_url: str = "https://www.whatnot.com/login"
    browse_url: str = "https://www.whatnot.com/live"

    def validate(self) -> tuple[bool, str]:
        """Validate the configuration."""
        if self.browser not in ["chrome", "firefox", "safari"]:
            return False, "Browser must be 'chrome', 'firefox', or 'safari'"

        if self.login_method not in ["credentials", "google"]:
            return False, "Login method must be 'credentials' or 'google'"

        if self.login_method == "credentials":
            if not self.email:
                return False, "Email is required for credentials login"
            if not self.password:
                return False, "Password is required for credentials login"

        return True, "Configuration valid"
