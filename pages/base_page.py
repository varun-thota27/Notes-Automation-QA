from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.logger import get_logger
import time
from selenium.common.exceptions import NoSuchElementException
from ai_engine.agents.healing_agent import HealingAgent
logger = get_logger(__name__)


class BasePage:
    """Common Selenium helper methods shared by all page objects."""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def find_element(self, by, value):

        try:

            return self.wait.until(
                EC.presence_of_element_located((by, value))
            )

        except Exception as e:

            logger.warning(
                f"[Healing Agent] "
                f"Locator failed: [{by}] '{value}'"
            )

            try:

                healing_agent = HealingAgent()

                healed_locator = healing_agent.heal_locator(

                    locator=(by, value),

                    driver=self.driver,

                    error_message=str(e)

                )

                logger.info(
                    f"[Healing Agent] "
                    f"Suggested Locator:\n{healed_locator}"
                )

            except Exception as healing_error:

                logger.error(
                    f"[Healing Agent Error] "
                    f"{healing_error}"
                )

            raise e

    def find_clickable(self, by, value):
        return self.wait.until(EC.element_to_be_clickable((by, value)))

    def find_elements(self, by, value):
        return self.driver.find_elements(by, value)

    def click(self, by, value):
        element = self.find_clickable(by, value)
        # Scroll element into view with extra scroll offset to clear ads
        self.driver.execute_script("""
            var elem = arguments[0];
            var y = elem.getBoundingClientRect().top + window.pageYOffset - 150;
            window.scrollTo({top: y, behavior: 'smooth'});
        """, element)
        time.sleep(1)
        self.wait.until(lambda d: element.is_displayed())
        try:
            element.click()
            logger.info(f"Clicked element: [{by}] '{value}'")
        except Exception as e:
            # If regular click fails (e.g., intercepted), use JavaScript click
            logger.warning(f"Regular click failed, using JavaScript click: {e}")
            self.driver.execute_script("arguments[0].click();", element)
            logger.info(f"Clicked element via JavaScript: [{by}] '{value}'")

    def type_text(self, by, value, text: str):
        element = self.find_element(by, value)
        element.clear()
        element.send_keys(text)
        logger.info(f"Typed '{text[:50]}' into [{by}] '{value}'")

    def get_text(self, by, value) -> str:
        return self.find_element(by, value).text

    def is_element_present(self, by, value, timeout: int = 5) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return True
        except Exception:
            return False

    def is_element_visible(self, by, value, timeout: int = 5) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((by, value))
            )
            return True
        except Exception:
            return False

    def get_current_url(self) -> str:
        return self.driver.current_url

    def refresh_page(self):
        self.driver.refresh()
        logger.info("Page refreshed")

    
