"""
test_notes_e2e.py — End-to-end test suite combining UI (Selenium) and API (requests).

Test Cases:
  TC-05   UI-to-API data consistency
  TC-06   API deletion reflects in UI after refresh
  TC-14.1 UI error message when API fails during note creation
  TC-14.2 UI stability when API fails during data fetch (notes load)
  TC-14.3 UI handles API timeout gracefully
"""

import time
import pytest
import allure
from unittest.mock import patch, MagicMock
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import requests as requests_lib

from pages.login_page import LoginPage
from pages.notes_page import NotesPage
from api.api_client import APIClient
from utils.logger import get_logger

logger = get_logger(__name__)


@pytest.mark.e2e
@allure.feature("E2E Tests")
class TestNotesE2E:

    # ------------------------------------------------------------------ #
    #  TC-05 — UI-to-API data consistency                                 #
    # ------------------------------------------------------------------ #

    @allure.story("TC-05: UI-to-API Data Consistency")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_tc05_ui_to_api_data_consistency(self, logged_in_driver, api_client, config):
        """Verify a note created in the UI appears in the API with matching data."""
        logger.info("=== TC-05: UI-to-API data consistency ===")

        driver = logged_in_driver
        notes_page = NotesPage(driver)

        unique_suffix = int(time.time())
        title = f"E2E Consistency Test {unique_suffix}"
        description = "Checking UI vs API data match"
        category = "Work"

        # Step 1: Create note via UI
        notes_page.create_note(title, description, category)
        time.sleep(2)
        assert notes_page.is_note_visible(title), \
            "Note not visible in UI after creation"
        logger.info("Step 1 PASS — Note created and visible in UI")

        # Step 2: Fetch notes from API and find the created note
        response = api_client.get_notes()
        assert response.status_code == 200, \
            f"GET /notes failed: {response.status_code}"

        notes = response.json()["data"]
        matched = [n for n in notes if n["title"] == title]
        assert len(matched) > 0, \
            f"Note with title '{title}' not found via API"

        api_note = matched[0]
        logger.info(f"Step 2 PASS — Note found via API: {api_note}")

        # Step 3: Compare fields
        assert api_note["title"] == title, \
            f"Title mismatch: UI='{title}' | API='{api_note['title']}'"
        assert api_note["description"] == description, \
            f"Description mismatch: UI='{description}' | API='{api_note['description']}'"
        assert api_note["category"] == category, \
            f"Category mismatch: UI='{category}' | API='{api_note['category']}'"
        logger.info("Step 3 PASS — All fields match between UI and API")

        # Cleanup
        api_client.delete_note(api_note["id"])
        logger.info("TC-05 PASSED")

    # ------------------------------------------------------------------ #
    #  TC-06 — API deletion reflects in UI                                #
    # ------------------------------------------------------------------ #

    @allure.story("TC-06: API Deletion Sync")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_tc06_api_deletion_reflects_in_ui(self, logged_in_driver, api_client, config):
        """Verify a note deleted via API is no longer visible in the UI after refresh."""
        logger.info("=== TC-06: API deletion → UI sync ===")

        driver = logged_in_driver
        notes_page = NotesPage(driver)

        # Step 1: Create note via API
        title = f"API Delete Sync Test {int(time.time())}"
        create_resp = api_client.create_note(title, "Will be deleted via API", "Home")
        assert create_resp.status_code in (200, 201), \
            f"Note creation failed: {create_resp.text}"
        note_id = create_resp.json()["data"]["id"]
        logger.info(f"Step 1 PASS — Note created via API: ID={note_id}")

        # Step 2: Refresh UI and verify note is present
        driver.refresh()
        time.sleep(2)
        assert notes_page.is_note_visible(title), \
            "Note not visible in UI after creation (pre-delete check)"
        logger.info("Step 2 PASS — Note visible in UI before deletion")

        # Step 3: Delete via API
        del_resp = api_client.delete_note(note_id)
        assert del_resp.status_code == 200, \
            f"API deletion failed: {del_resp.status_code} {del_resp.text}"
        logger.info(f"Step 3 PASS — Note deleted via API: ID={note_id}")

        # Step 4: Refresh UI and verify note is gone
        driver.refresh()
        time.sleep(2)
        assert not notes_page.is_note_visible(title), \
            f"Deleted note '{title}' still visible in UI after refresh"
        logger.info("Step 4 PASS — Deleted note no longer in UI")
        logger.info("TC-06 PASSED")

   