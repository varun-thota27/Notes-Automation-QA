import requests
import time
import json
import allure
from api.endpoints import Endpoints
from utils.logger import get_logger

logger = get_logger(__name__)


class APIClient:
    """Core API interaction layer using the requests library."""

    def __init__(self, base_url: str, token: str = None):
        self.base_url = base_url
        self.token = token
        self.session = requests.Session()

    # ------------------------------------------------------------------ #
    #  Internal helpers                                                    #
    # ------------------------------------------------------------------ #

    def _attach_response_to_allure(self, method: str, url: str, status_code: int, response_body: str):
        """Attach API response details to Allure report."""
        try:
            response_data = f"Method: {method}\nURL: {url}\nStatus: {status_code}\n\nResponse Body:\n{response_body}"
            allure.attach(response_data, name=f"{method}_{status_code}", attachment_type=allure.attachment_type.TEXT)
        except Exception as e:
            logger.debug(f"Could not attach response to Allure: {e}")

    def _headers(self, token=None):
        headers = {"Content-Type": "application/json"}
        t = token or self.token
        if t:
            headers["x-auth-token"] = t
        return headers

    # ------------------------------------------------------------------ #
    #  Generic HTTP verbs                                                  #
    # ------------------------------------------------------------------ #

    def get(self, endpoint: str, token=None, **kwargs):
        url = f"{self.base_url}{endpoint}"
        logger.info(f"GET {url}")
        response = self.session.get(url, headers=self._headers(token), **kwargs)
        logger.info(f"Response [{response.status_code}]")
        self._attach_response_to_allure("GET", url, response.status_code, response.text[:500])
        return response

    def post(self, endpoint: str, data: dict = None, token=None, **kwargs):
        url = f"{self.base_url}{endpoint}"
        logger.info(f"POST {url} | Body: {data}")
        response = self.session.post(url, json=data, headers=self._headers(token), **kwargs)
        logger.info(f"Response [{response.status_code}]: {response.text[:200]}")
        self._attach_response_to_allure("POST", url, response.status_code, response.text[:500])
        return response

    def patch(self, endpoint: str, data: dict = None, token=None, **kwargs):
        url = f"{self.base_url}{endpoint}"
        logger.info(f"PATCH {url} | Body: {data}")
        response = self.session.patch(url, json=data, headers=self._headers(token), **kwargs)
        logger.info(f"Response [{response.status_code}]")
        self._attach_response_to_allure("PATCH", url, response.status_code, response.text[:500])
        return response

    def delete(self, endpoint: str, token=None, **kwargs):
        url = f"{self.base_url}{endpoint}"
        logger.info(f"DELETE {url}")
        response = self.session.delete(url, headers=self._headers(token), **kwargs)
        logger.info(f"Response [{response.status_code}]")
        self._attach_response_to_allure("DELETE", url, response.status_code, response.text[:500])
        return response

    # ------------------------------------------------------------------ #
    #  User operations                                                     #
    # ------------------------------------------------------------------ #

    def register_user(self, name: str, email: str, password: str):
        logger.info(f"Registering user: {email}")
        return self.post(Endpoints.REGISTER, {
            "name": name,
            "email": email,
            "password": password
        })

    def login_user(self, email: str, password: str):
        logger.info(f"Logging in user: {email}")
        return self.post(Endpoints.LOGIN, {
            "email": email,
            "password": password
        })

    def delete_account(self):
        logger.info("Deleting current user account")
        return self.delete(Endpoints.DELETE_ACCOUNT)

    def get_profile(self):
        return self.get(Endpoints.PROFILE)

    # ------------------------------------------------------------------ #
    #  Notes operations                                                    #
    # ------------------------------------------------------------------ #

    def create_note(self, title: str, description: str, category: str = "Home"):
        logger.info(f"Creating note: title='{title}', category='{category}'")
        return self.post(Endpoints.NOTES, {
            "title": title,
            "description": description,
            "category": category
        })

    def get_notes(self):
        return self.get(Endpoints.NOTES)

    def get_note_by_id(self, note_id: str):
        return self.get(Endpoints.NOTE_BY_ID.format(note_id=note_id))

    def update_note(self, note_id: str, data: dict):
        return self.patch(Endpoints.NOTE_BY_ID.format(note_id=note_id), data)

    def delete_note(self, note_id: str):
        logger.info(f"Deleting note: {note_id}")
        return self.delete(Endpoints.NOTE_BY_ID.format(note_id=note_id))

    # ------------------------------------------------------------------ #
    #  Health                                                              #
    # ------------------------------------------------------------------ #

    def health_check(self):
        return self.get(Endpoints.HEALTH_CHECK)
