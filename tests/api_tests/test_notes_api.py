"""
test_notes_api.py — API test suite using the requests library.

Test Cases:
  TC-07  API response time < 2 seconds (5 consecutive calls)
  TC-09  Invalid / missing token returns HTTP 401
  TC-10  Duplicate note creation handled without data conflict
  TC-11  Large data input handled correctly
  TC-12  Concurrent note creation (5 threads) — all notes saved correctly
"""

import time
import pytest
import allure
import concurrent.futures

from api.api_client import APIClient
from utils.logger import get_logger

logger = get_logger(__name__)


@pytest.mark.api
@allure.feature("API Tests")
class TestNotesAPI:

    # ------------------------------------------------------------------ #
    #  TC-07 — API response time                                          #
    # ------------------------------------------------------------------ #

    @allure.story("TC-07: API Response Time")
    @allure.severity(allure.severity_level.NORMAL)
    def test_tc07_api_response_time(self, api_client, config):
        """Verify GET /notes responds in under 2 seconds for 5 consecutive calls."""
        logger.info("=== TC-07: API response time ===")

        limit = config.get_response_time_limit()
        num_requests = 5
        response_times = []

        for i in range(num_requests):
            start = time.time()
            response = api_client.get_notes()
            elapsed = time.time() - start
            response_times.append(elapsed)
            logger.info(f"Request {i + 1}: {elapsed:.3f}s | Status: {response.status_code}")
            assert response.status_code == 200, \
                f"Unexpected status code on request {i + 1}: {response.status_code}"

        avg = sum(response_times) / len(response_times)
        maximum = max(response_times)
        logger.info(f"Average: {avg:.3f}s | Max: {maximum:.3f}s | Limit: {limit}s")

        assert maximum < limit, \
            f"Max response time {maximum:.3f}s exceeded {limit}s limit"
        logger.info("TC-07 PASSED")

    # ------------------------------------------------------------------ #
    #  TC-09 — Invalid / missing token                                    #
    # ------------------------------------------------------------------ #

    @allure.story("TC-09: Invalid Token Handling")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_tc09_invalid_token_rejected(self, config):
        """Verify API returns 401 for invalid or missing authentication token."""
        logger.info("=== TC-09: Invalid / missing token handling ===")

        base_url = config.get_api_base_url()

        # Test 1: Invalid token value
        bad_client = APIClient(base_url, token="this_is_not_a_real_token_12345")
        response = bad_client.get_notes()
        logger.info(f"Invalid token → {response.status_code}: {response.text[:120]}")
        assert response.status_code == 401, \
            f"Expected 401 for invalid token, got {response.status_code}"
        logger.info("Step 1 PASS — Invalid token rejected with 401")

        # Test 2: No token at all
        anon_client = APIClient(base_url, token=None)
        response2 = anon_client.get_notes()
        logger.info(f"Missing token → {response2.status_code}: {response2.text[:120]}")
        assert response2.status_code == 401, \
            f"Expected 401 for missing token, got {response2.status_code}"
        logger.info("Step 2 PASS — Missing token rejected with 401")

        logger.info("TC-09 PASSED")

    # ------------------------------------------------------------------ #
    #  TC-10 — Duplicate note creation                                    #
    # ------------------------------------------------------------------ #

    @allure.story("TC-10: Duplicate Note Handling")
    @allure.severity(allure.severity_level.NORMAL)
    def test_tc10_duplicate_note_handling(self, api_client):
        """Verify duplicate note submissions are handled without unintended data conflicts."""
        logger.info("=== TC-10: Duplicate note handling ===")

        title = f"Duplicate Note TC10 {int(time.time())}"
        description = "Checking duplicate note behaviour"
        category = "Home"

        # First note
        r1 = api_client.create_note(title, description, category)
        assert r1.status_code in (200, 201), f"First note creation failed: {r1.text}"
        note_id_1 = r1.json()["data"]["id"]
        logger.info(f"Step 1 PASS — First note created, ID={note_id_1}")

        # Immediate duplicate submission
        r2 = api_client.create_note(title, description, category)
        logger.info(f"Duplicate submission → {r2.status_code}: {r2.text[:200]}")

        if r2.status_code in (200, 201):
            note_id_2 = r2.json()["data"]["id"]
            assert note_id_1 != note_id_2, \
                "Duplicate note has the SAME ID as original — data integrity issue"
            logger.info(f"Step 2 PASS — Duplicate allowed but with unique ID={note_id_2}")
            api_client.delete_note(note_id_2)
        else:
            logger.info(f"Step 2 PASS — Duplicate was rejected with status {r2.status_code}")

        # Cleanup
        api_client.delete_note(note_id_1)
        logger.info("TC-10 PASSED")

    # ------------------------------------------------------------------ #
    #  TC-13 — DELETE API with invalid note ID                           #
    # ------------------------------------------------------------------ #

    @allure.story("TC-13: Delete Invalid Note")
    @allure.severity(allure.severity_level.NORMAL)
    def test_tc13_delete_invalid_note_id(self, api_client):
        """Verify DELETE API returns validation error for invalid note ID."""

        logger.info("=== TC-13: DELETE invalid note ID ===")

        invalid_note_id = "invalid-note-id-99999"

        response = api_client.delete_note(invalid_note_id)

        assert response.status_code in [400, 404], \
            f"Unexpected status code: {response.status_code}"

        logger.info(f"API returned expected status: {response.status_code}")
        logger.info("TC-13 PASSED")