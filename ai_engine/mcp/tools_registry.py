class MCPToolsRegistry:

    AVAILABLE_TOOLS = {

        "locator_healing":
            "Suggest improved XPath/CSS locators",

        "failure_analysis":
            "Analyze Selenium failures",

        "retry_decision":
            "Determine whether retry is needed",

        "wait_strategy":
            "Suggest intelligent waits"

    }


    @staticmethod
    def get_tools():

        return MCPToolsRegistry.AVAILABLE_TOOLS