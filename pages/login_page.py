from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger(__name__)


class LoginPage(BasePage):
    """Page Object Model for the Login page."""

    # --- Locators ---
    EMAIL_INPUT    = (By.ID, "email")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON   = (By.CSS_SELECTOR, "button[type='submit']")
    ERROR_MESSAGE  = (By.CSS_SELECTOR, ".alert-danger")
    ALERT_MESSAGE = (By.CSS_SELECTOR, '[data-testid="alert-message"]')

    # ------------------------------------------------------------------ #

    def navigate(self, base_url: str):
        url = f"{base_url}/login"
        self.driver.get(url)
        logger.info(f"Navigated to login page: {url}")

    def enter_email(self, email: str):
        self.type_text(*self.EMAIL_INPUT, email)

    def enter_password(self, password: str):
        self.type_text(*self.PASSWORD_INPUT, password)

    def click_login(self):
        self.click(*self.LOGIN_BUTTON)
        logger.info("Login button clicked")

    def login(self, email: str, password: str):
        logger.info(f"Logging in as: {email}")
        self.enter_email(email)
        self.enter_password(password)
        self.click_login()

    def get_error_message(self) -> str:
        """Return login error message text."""
        return self.find_element(*self.ALERT_MESSAGE).text.strip()

    def is_error_displayed(self) -> bool:
        """Check whether login error toast is displayed."""
        return self.is_element_present(*self.ALERT_MESSAGE, timeout=5)
