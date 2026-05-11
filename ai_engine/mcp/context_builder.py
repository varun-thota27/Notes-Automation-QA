class MCPContextBuilder:

    @staticmethod
    def build_locator_context(

        locator,
        page_source,
        current_url,
        error_message

    ):

        return {

            "failed_locator": str(locator),

            "current_url": current_url,

            "error_message": error_message,

            "page_source": page_source[:15000]

        }