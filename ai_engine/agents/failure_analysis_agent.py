from ai_engine.llm.longcat_client import LongCatClient
from ai_engine.llm.prompts import LLMPrompts

from utils.logger import get_logger

logger = get_logger(__name__)


class FailureAnalysisAgent:
    """
    Analyzes test failures using LLM to provide root cause analysis
    and suggested fixes.
    """

    def __init__(self):
        """Initialize the failure analysis agent with LLM client."""
        try:
            self.client = LongCatClient()
            logger.debug("[FailureAnalysisAgent] Initialized successfully")
        except Exception as e:
            logger.error(f"[FailureAnalysisAgent] Failed to initialize LLM client: {e}")
            self.client = None


    def analyze_failure(self, test_name, error_message):
        """
        Analyze a test failure using LLM.
        
        Args:
            test_name: Name of the failed test
            error_message: Full error/stacktrace message
            
        Returns:
            str: LLM analysis response or None if analysis failed
        """
        if not self.client:
            logger.error("[FailureAnalysisAgent] LLM client not initialized")
            return None

        try:
            logger.info(f"[FailureAnalysisAgent] Analyzing failure for: {test_name}")
            
            prompt = LLMPrompts.failure_analysis_prompt(
                error=error_message,
                test_name=test_name
            )

            response = self.client.ask_llm(prompt)

            if not response:
                logger.warning("[FailureAnalysisAgent] Empty response from LLM")
                return None

            logger.info(
                f"[AI FAILURE ANALYSIS] Successfully analyzed {test_name}:\n"
                f"{response}"
            )

            return response

        except Exception as e:
            logger.error(
                f"[FailureAnalysisAgent] Error analyzing failure: {e}",
                exc_info=True
            )
            return None