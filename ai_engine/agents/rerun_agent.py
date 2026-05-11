class RerunAgent:

    RETRYABLE_ERRORS = [

        "TimeoutException",

        "StaleElementReferenceException",

        "ElementClickInterceptedException",

        "SessionNotCreatedException"
    ]


    @staticmethod
    def should_rerun(error_message):

        for error in RerunAgent.RETRYABLE_ERRORS:

            if error in error_message:

                return True

        return False