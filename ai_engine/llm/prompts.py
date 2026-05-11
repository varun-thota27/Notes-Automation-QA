class LLMPrompts:

    @staticmethod
    def locator_healing_prompt(locator, html):
        """Generate prompt for locator healing via LLM."""
        return f"""
You are a Selenium locator healing assistant.

The following locator failed:

{locator}

Analyze the HTML and suggest:

1. Better XPath
2. Better CSS selector

HTML:
{html}

Return concise output only.
"""

    @staticmethod
    def failure_analysis_prompt(error, test_name):
        """Generate prompt for failure analysis via LLM."""
        return f"""
You are a Selenium automation debugging assistant.

Analyze this failure.

Test Name:
{test_name}

Error:
{error}

Provide:

1. Root Cause
2. Suggested Fix
3. Retry Recommendation
4. Stability Improvement Suggestion

Keep response concise.
"""