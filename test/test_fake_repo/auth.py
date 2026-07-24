"""Module for handling user security and input validation."""
from typing import Union

def clean_input(raw_text: str) -> str:
    """Sanitizes user input strings to prevent basic injection patterns.
    
    This function removes typical bad characters and strips trailing whitespaces.
    """
    if not raw_text:
        return ""
    return raw_text.strip().replace("'", "").replace('"', "")


def generate_session_token(user_id: int, scope: Union[str, None]) -> str:
    """Generates a secure mock token bound to a specific user and access scope."""
    safe_scope = scope if scope else "guest"
    return f"token_usr_{user_id}_{safe_scope}"