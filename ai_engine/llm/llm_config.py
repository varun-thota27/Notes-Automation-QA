import json
import os


class LLMConfig:

    @staticmethod
    def load_config():

        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "config",
            "ai_config.json"
        )

        with open(config_path, "r") as file:
            return json.load(file)