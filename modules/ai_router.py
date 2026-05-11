"""Route chat requests to the local Qwen nutrition model."""

from modules import llama_handler


def get_response(user_input: str, history: list, profile: dict, detected_foods=None) -> str:
    return llama_handler.generate(user_input, history, profile, detected_foods=detected_foods or [])
