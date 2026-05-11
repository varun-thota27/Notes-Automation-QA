import json
import os

from ai_engine.llm.longcat_client import LongCatClient
from ai_engine.llm.prompts import LLMPrompts
from ai_engine.mcp.context_builder import MCPContextBuilder
from utils.logger import get_logger

logger = get_logger(__name__)


class HealingAgent:
    """
    Heals broken Selenium locators using LLM analysis.
    Stores healed locators in memory for future reuse.
    """

    def __init__(self):
        """Initialize the healing agent with LLM client."""
        try:
            self.client = LongCatClient()
            self.memory_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "memory",
                "healed_locators.json"
            )
            logger.debug("[HealingAgent] Initialized successfully")
        except Exception as e:
            logger.error(f"[HealingAgent] Failed to initialize: {e}")
            self.client = None


    def heal_locator(self, locator, driver, error_message):
        """
        Heal a broken locator using LLM analysis.
        
        Args:
            locator: The failed locator
            driver: Selenium WebDriver instance
            error_message: Error message from locator failure
            
        Returns:
            str: Suggested healed locator or None if healing failed
        """
        if not self.client:
            logger.error("[HealingAgent] LLM client not initialized")
            return None

        try:
            logger.info(f"[HealingAgent] Attempting to heal locator: {locator}")
            
            context = MCPContextBuilder.build_locator_context(
                locator=locator,
                page_source=driver.page_source,
                current_url=driver.current_url,
                error_message=error_message
            )

            prompt = LLMPrompts.locator_healing_prompt(
                locator=context["failed_locator"],
                html=context["page_source"]
            )

            response = self.client.ask_llm(prompt)

            if not response:
                logger.warning("[HealingAgent] Empty response from LLM")
                return None

            logger.info(f"[HealingAgent] Healed locator suggestion: {response}")
            
            self.save_healed_locator(locator, response)
            return response

        except Exception as e:
            logger.error(
                f"[HealingAgent] Error healing locator: {e}",
                exc_info=True
            )
            return None


    def save_healed_locator(self, old_locator, new_locator):
        """
        Save healed locator to memory for future reuse.
        
        Args:
            old_locator: Original failed locator
            new_locator: LLM-suggested healed locator
        """
        if not new_locator:
            logger.warning("[HealingAgent] Skipping save - new_locator is None/empty")
            return

        try:
            data = {}

            if os.path.exists(self.memory_path):
                with open(self.memory_path, "r") as file:
                    data = json.load(file)

            data[str(old_locator)] = new_locator

            with open(self.memory_path, "w") as file:
                json.dump(data, file, indent=4)

            logger.debug(
                f"[HealingAgent] Saved healed locator mapping: "
                f"{old_locator} → {new_locator}"
            )
        except Exception as e:
            logger.error(
                f"[HealingAgent] Error saving healed locator: {e}",
                exc_info=True
            )