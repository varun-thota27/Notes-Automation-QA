from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class WaitUtils:

    @staticmethod
    def wait_for_element(driver, locator, timeout=15):

        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(locator)
        )


    @staticmethod
    def wait_for_clickable(driver, locator, timeout=15):

        return WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(locator)
        )


    @staticmethod
    def wait_for_page_ready(driver, timeout=15):

        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script(
                "return document.readyState"
            ) == "complete"
        )