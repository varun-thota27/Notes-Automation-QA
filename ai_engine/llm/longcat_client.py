from urllib import response

import requests

from ai_engine.llm.llm_config import LLMConfig


class LongCatClient:

    def __init__(self):

        config = LLMConfig.load_config()

        self.api_key = config["longcat_api_key"]
        self.base_url = config["base_url"]
        self.model = config["model"]


    def ask_llm(self, prompt):

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3
        }

        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )

        response.raise_for_status()
        print("\n========== RAW LONGCAT RESPONSE ==========\n")
        print(response.text)
        data = response.json()

        return data["choices"][0]["message"]["content"]