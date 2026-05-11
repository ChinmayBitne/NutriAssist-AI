"""
llama_handler.py
Qwen-based nutrition assistant inference using BASE MODEL + LORA ADAPTER.
- Downloads base model and adapter once locally via snapshot_download
- Loads model once per Streamlit process via st.cache_resource
- Supports 4-bit loading for consumer GPUs like RTX 4060
- Uses chat template correctly for Qwen models
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import streamlit as st
import torch
from huggingface_hub import snapshot_download
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

os.environ.setdefault("HF_HUB_VERBOSITY", "error")
os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

HF_TOKEN = os.getenv("HF_TOKEN")
BASE_MODEL_ID = os.getenv("BASE_MODEL_ID", "Qwen/Qwen2.5-3B-Instruct")
ADAPTER_MODEL_ID = os.getenv("ADAPTER_MODEL_ID", "xdna14/nutrition-bot-qwen25-3b-v7-adapter")
MODEL_CACHE_DIR = os.getenv("MODEL_CACHE_DIR", str(Path.home() / ".cache" / "nutriassist" / "models"))
USE_4BIT = os.getenv("USE_4BIT", "true").strip().lower() in {"1", "true", "yes", "on"}
MAX_INPUT_TOKENS = int(os.getenv("MAX_INPUT_TOKENS", "2048"))
MAX_NEW_TOKENS = int(os.getenv("MAX_NEW_TOKENS", "220"))

SYSTEM_PROMPT = (
    "You are a friendly nutrition assistant. "
    "Answer clearly and naturally. "
    "Give practical, general nutrition guidance. "
    "Use food facts from the prompt when they are provided. "
    "Do not assume the user's age, weight, disease, or goals unless the user explicitly states them. "
    "If details are missing, say that it depends on portion size, ingredients, or personal goals. "
    "Do not diagnose disease or replace a doctor or dietitian."
)


def _hf_kwargs() -> dict[str, Any]:
    return {"token": HF_TOKEN} if HF_TOKEN else {}


def _safe_local_dir(repo_id: str) -> str:
    return os.path.join(MODEL_CACHE_DIR, repo_id.replace("/", "__"))


@st.cache_resource(show_spinner=True)
def ensure_models_downloaded() -> tuple[str, str]:
    os.makedirs(MODEL_CACHE_DIR, exist_ok=True)
    base_dir = snapshot_download(
        repo_id=BASE_MODEL_ID,
        local_dir=_safe_local_dir(BASE_MODEL_ID),
        **_hf_kwargs(),
    )
    adapter_dir = snapshot_download(
        repo_id=ADAPTER_MODEL_ID,
        local_dir=_safe_local_dir(ADAPTER_MODEL_ID),
        **_hf_kwargs(),
    )
    return base_dir, adapter_dir


@st.cache_resource(show_spinner=True)
def load_model_and_tokenizer():
    base_dir, adapter_dir = ensure_models_downloaded()

    tokenizer = AutoTokenizer.from_pretrained(base_dir, use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"

    load_kwargs: dict[str, Any] = {
        "device_map": "auto",
        "low_cpu_mem_usage": True,
    }

    if torch.cuda.is_available():
        if USE_4BIT:
            load_kwargs["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=torch.float16,
            )
        else:
            load_kwargs["torch_dtype"] = torch.float16
    else:
        load_kwargs["torch_dtype"] = torch.float32

    base_model = AutoModelForCausalLM.from_pretrained(base_dir, **load_kwargs)
    model = PeftModel.from_pretrained(base_model, adapter_dir)
    model.eval()
    return model, tokenizer


def _compact_profile(profile: dict[str, Any] | None) -> str:
    if not profile:
        return ""
    parts = []
    allowed_keys = ["Age", "Weight", "Height", "Blood Type", "Conditions", "Goal", "Gender"]
    for key in allowed_keys:
        value = profile.get(key)
        if value not in (None, "", [], {}):
            parts.append(f"{key}: {value}")
    return "; ".join(parts)


IMAGE_REFERENCE_TERMS = {
    "this", "that", "it", "meal", "food", "dish", "plate", "image", "photo", "picture", "uploaded"
}


def _should_use_image_context(user_input: str, detected_foods: list[str] | None) -> bool:
    if not detected_foods:
        return False
    text = user_input.lower()
    if any(food.lower() in text for food in detected_foods):
        return True
    return any(term in text.split() for term in IMAGE_REFERENCE_TERMS) or any(
        phrase in text for phrase in [
            "this meal", "that meal", "this food", "that food", "this dish", "that dish",
            "in the image", "from the image", "from the photo", "uploaded image", "uploaded meal",
            "is it healthy", "is this healthy", "can i eat this", "should i eat this",
        ]
    )



def _build_messages(
    user_input: str,
    history: list[dict[str, str]] | None,
    profile: dict[str, Any] | None,
    detected_foods: list[str] | None = None,
) -> list[dict[str, str]]:
    system_parts = [SYSTEM_PROMPT]
    profile_text = _compact_profile(profile)
    if profile_text:
        system_parts.append(f"User profile: {profile_text}.")
    if _should_use_image_context(user_input, detected_foods):
        system_parts.append(
            "Image food context for this turn only: " + ", ".join(detected_foods) + "."
        )

    messages: list[dict[str, str]] = [{"role": "system", "content": " ".join(system_parts)}]

    recent = history[-8:] if history else []
    for msg in recent:
        role = msg.get("role", "user")
        content = (msg.get("content") or "").strip()
        if role in {"user", "assistant"} and content:
            messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": user_input.strip()})
    return messages



def warmup() -> None:
    load_model_and_tokenizer()



def generate(
    user_input: str,
    history: list[dict[str, str]] | None,
    profile: dict[str, Any] | None,
    detected_foods: list[str] | None = None,
) -> str:
    try:
        model, tokenizer = load_model_and_tokenizer()
    except Exception as exc:
        return f"Sorry, the model failed to load: {exc}"

    messages = _build_messages(user_input, history or [], profile or {}, detected_foods or [])
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=MAX_INPUT_TOKENS)

    if torch.cuda.is_available():
        try:
            inputs = {k: v.to("cuda") for k, v in inputs.items()}
        except Exception:
            pass

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=True,
            temperature=0.3,
            top_p=0.85,
            repetition_penalty=1.08,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
            use_cache=True,
        )

    prompt_len = inputs["input_ids"].shape[1]
    response = tokenizer.decode(outputs[0][prompt_len:], skip_special_tokens=True).strip()
    return response or "I'm sorry, I couldn't generate a response. Please try again."
