from ai_engine.llm.longcat_client import LongCatClient


class AIDataAgent:

    def __init__(self):

        self.client = LongCatClient()


    def generate_note_data(self):

        prompt = """
Generate realistic test data for a notes application.

Return:
1. title
2. description
3. category

Keep response concise.
"""

        return self.client.ask_llm(prompt)