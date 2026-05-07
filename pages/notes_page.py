from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger(__name__)


class NotesPage(BasePage):
    """Page Object Model for the Notes dashboard."""

    # --- Locators ---
    ADD_NOTE_BTN    = (By.CSS_SELECTOR, '[data-testid="add-new-note"]')
    NOTE_CATEGORY   = (By.CSS_SELECTOR, '[data-testid="note-category"]')
    NOTE_TITLE      = (By.CSS_SELECTOR, '[data-testid="note-title"]')
    NOTE_DESCRIPTION= (By.CSS_SELECTOR, '[data-testid="note-description"]')
    NOTE_SUBMIT     = (By.CSS_SELECTOR, '[data-testid="note-submit"]')
    NOTE_CANCEL     = (By.CSS_SELECTOR, '[data-testid="note-cancel"]')
    NOTE_CARD       = (By.CSS_SELECTOR, '[data-testid="note-card"]')
    NOTE_DELETE     = (By.CSS_SELECTOR, '[data-testid="note-delete"]')
    NOTE_VIEW       = (By.CSS_SELECTOR, '[data-testid="note-view"]')
    LOGOUT_BTN      = (By.CSS_SELECTOR, '[data-testid="logout"]')
    SEARCH_INPUT    = (By.CSS_SELECTOR, '[data-testid="search-input"]')

    # ------------------------------------------------------------------ #

    def navigate(self, base_url: str):
        self.driver.get(base_url)
        logger.info(f"Navigated to notes dashboard: {base_url}")

    def click_add_note(self):
        self.click(*self.ADD_NOTE_BTN)
        logger.info("Opened Add Note modal")

    def select_category(self, category: str):
        select_el = self.find_element(*self.NOTE_CATEGORY)
        Select(select_el).select_by_visible_text(category)
        logger.info(f"Selected category: {category}")

    def enter_title(self, title: str):
        self.type_text(*self.NOTE_TITLE, title)

    def enter_description(self, description: str):
        self.type_text(*self.NOTE_DESCRIPTION, description)

    def click_submit(self):
        self.click(*self.NOTE_SUBMIT)
        logger.info("Clicked Create/Submit button")

    def click_cancel(self):
        self.click(*self.NOTE_CANCEL)
        logger.info("Clicked Cancel button")
    
    def click_save_note(self):
        """Alias for submit button."""
        self.click_submit()

    def create_note(self, title: str, description: str, category: str = "Home"):
        logger.info(f"Creating note — title='{title}' category='{category}'")
        self.click_add_note()
        self.select_category(category)
        self.enter_title(title)
        self.enter_description(description)
        self.click_submit()

    def get_note_cards(self) -> list:
        return self.find_elements(*self.NOTE_CARD)

    def get_note_count(self) -> int:
        return len(self.get_note_cards())

    def is_note_visible(self, title: str) -> bool:
        cards = self.get_note_cards()
        for card in cards:
            if title in card.text:
                return True
        return False

    def logout(self):
        self.click(*self.LOGOUT_BTN)
        logger.info("User logged out")
