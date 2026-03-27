"""
Routing layer for NutriAssist AI.

This module keeps the chat interface separated from the
generation logic so the application stays modular.
"""

from modules.llama_handler import generate


def get_response(user_input: str, history: list) -> str:
    """
    Return the assistant response for a user query.

    Args:
        user_input: Current user message.
        history: Previous chat messages.

    Returns:
        Assistant response text.
    """
    return generate(user_input, history)