import configparser
import os


class ConfigReader:
    """Reads configuration values from config/config.ini."""

    def __init__(self, config_path: str = None):
        self.config = configparser.ConfigParser()
        if config_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, "config", "config.ini")
        self.config.read(config_path)

    def get(self, section: str, key: str) -> str:
        return self.config.get(section, key)

    # --- App URLs ---
    def get_ui_url(self) -> str:
        return self.get("app", "ui_url")

    def get_api_base_url(self) -> str:
        return self.get("app", "api_base_url")

    # --- Test User ---
    # def get_test_name(self) -> str:
    #     return self.get("test_user", "name")

    def get_test_email(self) -> str:
        return self.get("credentials", "email")

    def get_test_password(self) -> str:
        return self.get("credentials", "password")

    # --- Settings ---
    def get_implicit_wait(self) -> int:
        return int(self.get("settings", "implicit_wait"))

    def get_page_load_timeout(self) -> int:
        return int(self.get("settings", "page_load_timeout"))

    def get_api_timeout(self) -> int:
        return int(self.get("settings", "api_timeout"))

    def get_response_time_limit(self) -> float:
        return float(self.get("settings", "response_time_limit"))

    def is_headless(self) -> bool:
        return self.get("settings", "headless").lower() == "true"

    # --- Selenium Grid ---
    def use_selenium_grid(self) -> bool:
        return self.get("selenium_grid", "use_grid").lower() == "true"

    def get_grid_hub_url(self) -> str:
        return self.get("selenium_grid", "grid_hub_url")

    def get_grid_browser(self) -> str:
        return self.get("selenium_grid", "grid_browser")

    def get_grid_timeout(self) -> int:
        return int(self.get("selenium_grid", "grid_timeout"))
