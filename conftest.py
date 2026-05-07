"""
conftest.py — Root-level pytest fixtures shared across all test modules.

Fixtures hierarchy:
  config (session)
    └── worker_id (session)        → xdist worker identifier
          └── auth_token (session) → login token (per-worker)
                └── api_client (session) → authenticated APIClient (per-worker)
  driver (function)               → Chrome WebDriver
    └── logged_in_driver (function) → driver already at the dashboard

Parallel Execution:
  pytest-xdist is enabled via `-n auto` in pytest.ini.
  Each worker spawns its own session fixtures to avoid race conditions.
"""

import uuid
import pytest
import allure
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from api.api_client import APIClient
from utils.config_reader import ConfigReader
from utils.logger import get_logger

logger = get_logger(__name__)

# Ensure screenshots folder exists at startup
SCREENSHOTS_DIR = os.path.join("screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

# Global storage for test status (to be set by pytest_runtest_logreport hook)
_test_status = {}


# ============================================================ #
#  Pytest Hooks                                                #
# ============================================================ #

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Automatically capture screenshot on test failure
    and attach it to Allure report.
    """

    outcome = yield
    report = outcome.get_result()

    # Capture screenshot only if actual test step fails
    if report.when == "call" and report.failed:

        driver = item.funcargs.get("driver", None)

        if driver:
            try:
                timestamp = datetime.now().strftime(
                    "%Y%m%d_%H%M%S_%f"
                )[:-3]

                screenshot_filename = (
                    f"{item.name}_{timestamp}_FAILED.png"
                )

                screenshot_path = os.path.join(
                    SCREENSHOTS_DIR,
                    screenshot_filename
                )

                # Save screenshot
                driver.save_screenshot(screenshot_path)

                logger.error(
                    f"[FAILED TEST] Screenshot captured: "
                    f"{screenshot_path}"
                )

                # Attach screenshot to Allure
                with open(screenshot_path, "rb") as image_file:
                    allure.attach(
                        image_file.read(),
                        name=screenshot_filename,
                        attachment_type=allure.attachment_type.PNG
                    )

            except Exception as e:
                logger.error(
                    f"Failed to capture screenshot on failure: {e}"
                )



# ============================================================ #
#  Allure Hooks & Fixtures                                     #
# ============================================================ #

@pytest.fixture(scope="function", autouse=True)
def attach_test_info(request):
    """Attach test information and metadata to Allure report."""
    # Add test name and description
    allure.dynamic.title(request.node.name)
    if request.node.obj.__doc__:
        allure.dynamic.description(request.node.obj.__doc__)
    
    # Add tags based on markers
    for marker in request.node.iter_markers():
        allure.dynamic.tag(marker.name)
    
    yield
    
    # Capture and attach logs after test
    try:
        log_file = os.path.join("reports", "test_logs.log")
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                allure.attach(f.read(), name="test_logs.log", attachment_type=allure.attachment_type.TEXT)
    except Exception as e:
        logger.debug(f"Could not attach logs: {e}")


@pytest.fixture(scope="function")
def take_screenshot(request):
    """On-demand screenshot fixture for use within tests.
    Usage: take_screenshot("step_name") to capture at any point during test.
    """
    def _take_screenshot(step_name: str = "screenshot"):
        try:
            driver = request.getfixturevalue('driver') if 'driver' in request.fixturenames else None
            if driver:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
                screenshot_filename = f"{request.node.name}_{step_name}_{timestamp}.png"
                screenshot_path = os.path.join(SCREENSHOTS_DIR, screenshot_filename)
                
                driver.save_screenshot(screenshot_path)
                logger.info(f"Screenshot captured: {screenshot_path}")
                
                # Attach to Allure report
                with open(screenshot_path, "rb") as f:
                    allure.attach(
                        f.read(),
                        name=screenshot_filename,
                        attachment_type=allure.attachment_type.PNG
                    )
                return screenshot_path
            else:
                logger.warning("Driver not available for screenshot")
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
    
    return _take_screenshot


# ============================================================ #
#  xdist Worker ID                                            #
# ============================================================ #

@pytest.fixture(scope="session")
def worker_id(request) -> str:
    """Return the xdist worker id, or 'master' when not running in parallel."""
    return getattr(request.config, "workerinput", {}).get("workerid", "master")


# ============================================================ #
#  Configuration                                               #
# ============================================================ #

@pytest.fixture(scope="session")
def config() -> ConfigReader:
    return ConfigReader()


@pytest.fixture(scope="session")
def ui_base_url(config) -> str:
    return config.get_ui_url()


@pytest.fixture(scope="session")
def api_base_url(config) -> str:
    return config.get_api_base_url()



# ============================================================ #
#  Auth token (session-scoped, xdist-safe per worker)          #
# ============================================================ #

@pytest.fixture(scope="session")
def auth_token(config, worker_id) -> str:
    """Obtain a login token per xdist worker to avoid shared-state race conditions."""
    client = APIClient(config.get_api_base_url())

    email = config.get_test_email()
    password = config.get_test_password()

    response = client.login_user(email, password)

    assert response.status_code == 200, (
        f"[Worker: {worker_id}] Login failed ({response.status_code}): {response.text}"
    )

    token = response.json()["data"]["token"]

    logger.info(f"[Setup][Worker: {worker_id}] Auth token obtained")
    return token

# ============================================================ #
#  Authenticated API client (session-scoped, xdist-safe)       #
# ============================================================ #

@pytest.fixture(scope="session")
def api_client(config, auth_token, worker_id) -> APIClient:
    """Authenticated API client, one instance per xdist worker."""
    logger.info(f"[Setup][Worker: {worker_id}] API client initialized")
    return APIClient(config.get_api_base_url(), token=auth_token)


# ============================================================ #
#  WebDriver (function-scoped — fresh browser per test)        #
# ============================================================ #

@pytest.fixture(scope="function")
def driver(config):
    """
    Creates WebDriver instance - either local Chrome or remote via Selenium Grid.
    Fixture scope remains 'function' (fresh driver per test).
    Grid mode is controlled via config: use_grid=true/false in config.ini
    """
    use_grid = config.use_selenium_grid()
    
    options = Options()
    if config.is_headless():
        options.add_argument("--headless=new")
    options.add_argument("--disable-save-password-bubble")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--start-maximized")
    
    # Existing stability options
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # Add options to prevent renderer timeouts
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-backgrounding-occluded-windows")
    options.add_argument("--disable-renderer-backgrounding")
    options.add_argument("--disable-features=TranslateUI")
    options.add_argument("--disable-ipc-flooding-protection")
    options.add_argument("--enable-features=NetworkService,NetworkServiceInProcess")
    options.add_argument("--max_old_space_size=4096")
    
    try:
        if use_grid:
            # Create remote WebDriver connected to Selenium Grid Hub
            grid_url = config.get_grid_hub_url()
            
            chrome = webdriver.Remote(
                command_executor=f"{grid_url}/wd/hub",
                options=options
            )
            logger.info(f"[Setup] Remote WebDriver connected to Grid: {grid_url}")
        else:
            # Create local Chrome WebDriver
            try:
                chromedriver_path = ChromeDriverManager().install()
                logger.info(f"[Setup] ChromeDriver path: {chromedriver_path}")
                service = Service(chromedriver_path)
                chrome = webdriver.Chrome(service=service, options=options)
            except Exception as e:
                logger.warning(f"[Setup] Failed to use webdriver-manager, trying direct Chrome: {e}")
                chrome = webdriver.Chrome(options=options)
            logger.info("[Setup] Local Chrome WebDriver started")
        
        chrome.implicitly_wait(config.get_implicit_wait())
        chrome.set_page_load_timeout(config.get_page_load_timeout())
        chrome.set_script_timeout(30)
        
        # Attach browser information to Allure report
        try:
            browser_info = chrome.capabilities
            allure.attach(
                f"Browser: {browser_info.get('browserName', 'Chrome')}\nVersion: {browser_info.get('browserVersion', 'N/A')}\nPlatform: {browser_info.get('platformName', 'N/A')}\nMode: {'Grid' if use_grid else 'Local'}",
                name="Browser Info",
                attachment_type=allure.attachment_type.TEXT
            )
        except Exception as e:
            logger.debug(f"Could not attach browser info: {e}")

        yield chrome

        chrome.quit()
        logger.info("[Teardown] WebDriver closed")
    
    except Exception as e:
        logger.error(f"[Setup] Failed to create WebDriver: {e}")
        raise


# ============================================================ #
#  Pre-logged-in driver (function-scoped)                      #
# ============================================================ #

@pytest.fixture(scope="function")
def logged_in_driver(driver, config):
    """Yield a driver that is already logged in and at the notes dashboard."""

    from pages.login_page import LoginPage

    email = config.get_test_email()
    password = config.get_test_password()

    login_page = LoginPage(driver)
    login_page.navigate(config.get_ui_url())
    login_page.login(email, password)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, '[data-testid="add-new-note"]')
        )
    )

    logger.info("[Setup] Driver logged in and dashboard ready")

    return driver