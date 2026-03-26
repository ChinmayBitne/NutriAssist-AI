from __future__ import annotations

import os
from pathlib import Path

import streamlit as st
import torch
from dotenv import load_dotenv
from huggingface_hub import snapshot_download
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
BASE_MODEL_ID = os.getenv("BASE_MODEL_ID", "Qwen/Qwen2.5-3B-Instruct")
MODEL_CACHE_DIR = os.getenv("MODEL_CACHE_DIR", str(Path.home() / ".cache" / "nutriassist" / "models"))
USE_4BIT = os.getenv("USE_4BIT", "true").strip().lower() in {"1", "true", "yes", "on"}
MAX_INPUT_TOKENS = int(os.getenv("MAX_INPUT_TOKENS", "1024"))
MAX_NEW_TOKENS = int(os.getenv("MAX_NEW_TOKENS", "120"))

SYSTEM_PROMPT = (
    "You are NutriAssist, a helpful nutrition chatbot. "
    "Answer clearly and simply. "
    "Give general nutrition guidance only. "
    "Do not diagnose disease or replace a doctor or dietitian."
)

def _hf_kwargs():
    return {"token": HF_TOKEN} if HF_TOKEN else {}

def _safe_local_dir(repo_id: str) -> str:
    return os.path.join(MODEL_CACHE_DIR, repo_id.replace("/", "__"))

@st.cache_resource(show_spinner=True)
def _download_and_load():
    os.makedirs(MODEL_CACHE_DIR, exist_ok=True)
    local_dir = snapshot_download(
        repo_id=BASE_MODEL_ID,
        local_dir=_safe_local_dir(BASE_MODEL_ID),
        **_hf_kwargs(),
    )

    tokenizer = AutoTokenizer.from_pretrained(local_dir, use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"

    load_kwargs = {"device_map": "auto", "low_cpu_mem_usage": True}
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

    model = AutoModelForCausalLM.from_pretrained(local_dir, **load_kwargs)
    model.eval()
    return model, tokenizer

def warmup():
    _download_and_load()

def generate(user_input: str, history: list) -> str:
    model, tokenizer = _download_and_load()

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history[-6:]:
        role = msg.get("role", "user")
        content = str(msg.get("content", "")).strip()
        if role in {"user", "assistant"} and content:
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": user_input})

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
            repetition_penalty=1.05,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
            use_cache=True,
        )

    prompt_len = inputs["input_ids"].shape[1]
    reply = tokenizer.decode(outputs[0][prompt_len:], skip_special_tokens=True).strip()
    return reply or "Sorry, I could not generate a response."
