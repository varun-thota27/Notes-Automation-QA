class Endpoints:
    """All API endpoint URL paths for the Notes application."""

    # --- User Endpoints ---
    REGISTER = "/users/register"
    LOGIN = "/users/login"
    PROFILE = "/users/me"
    DELETE_ACCOUNT = "/users/me"

    # --- Notes Endpoints ---
    NOTES = "/notes"
    NOTE_BY_ID = "/notes/{note_id}"

    # --- Health ---
    HEALTH_CHECK = "/health-check"
