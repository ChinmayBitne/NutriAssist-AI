from modules.llama_handler import generate

def get_response(user_input: str, history: list) -> str:
    return generate(user_input, history)
