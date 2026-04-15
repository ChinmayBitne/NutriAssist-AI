# 🥗 NutriAssist AI (V3)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-Latest-red) ![License](https://img.shields.io/badge/License-MIT-green)

NutriAssist AI is a conversational nutrition assistant that helps users ask questions about food, calories, macros, and healthier eating choices.

V3 combines two layers:
- a local chat model for natural conversation
- dataset grounding with optional fine-tuned LoRA behavior

This keeps responses practical, food-aware, and better aligned with nutrition use cases.

---

## 🚀 Overview

NutriAssist AI provides:

* 💬 A chat interface for nutrition-related questions
* 🤖 Local language model inference
* 🧠 Optional LoRA adapter support for fine-tuned response behavior
* 📊 Nutrition dataset lookup for grounded answers
* 🇮🇳 Better food coverage, including Indian dishes in the dataset
* ⚡ GPU-friendly inference with optional 4-bit loading
* 🧱 A modular structure ready for future features

---

## 🆕 What's New in V3

Compared to V2, this version adds and improves:

* Optional LoRA adapter loading through `ADAPTER_MODEL_ID`
* Fine-tuning-oriented response behavior in the model pipeline
* Updated UI copy and prompts focused on nutrition dialogue quality
* Continued grounding through `data/nutrients.csv`

V1 repository: [NutriAssist-AI (V1)](https://github.com/ChinmayBitne/NutriAssist-AI)

---

## 📈 Results: Before vs After Fine-tuning

In internal testing on food-oriented prompts, V3 responses were more aligned and practical than base-model-only outputs.

**Before fine-tuning (base model only):**
- More generic nutrition advice
- Less consistent handling of Indian food queries
- Weaker use of dataset-style factual framing

**After fine-tuning (V3 with optional adapter):**
- More task-aligned nutrition responses
- Better handling of common Indian meal questions
- Cleaner and more direct food guidance

> Note: Exact gains depend on the adapter used, prompt style, and hardware setup.

---

## 🧠 How It Works

```text
User Input -> Streamlit UI -> AI Router -> Nutrition Lookup -> Base Model (+ Optional LoRA Adapter) -> Response -> UI
```

### Core flow

1. User asks a nutrition-related question
2. The system searches `data/nutrients.csv` for matching foods
3. Nutrition facts are injected into prompt context
4. The base model generates a response (with optional LoRA adapter loaded)
5. The final answer is shown in the chat interface

---

## 📸 Demo

![Demo](assets/Demo.png)

---

## 🏗️ Architecture

### Main components

* **App.py**
  * Builds the Streamlit chatbot interface
  * Manages chat history in session state
  * Warms the model once at startup

* **modules/ai_router.py**
  * Routes user queries to the generation layer

* **modules/nutrition_lookup.py**
  * Loads and searches the nutrition dataset
  * Applies exact contains match + fuzzy fallback
  * Builds compact nutrition context for prompting

* **modules/llama_handler.py**
  * Downloads/caches base model from Hugging Face
  * Optionally downloads and loads a PEFT LoRA adapter
  * Runs generation with conversation + dataset context

* **notebook/Nutrition Assist Finetune Notebook.ipynb**
  * Fine-tuning workflow notebook used for adapter training experiments

---

## ✅ Prerequisites

Before you begin, ensure you have:

- **Python 3.10 or higher**
- **pip**
- **Git** (optional)
- **Hugging Face account** (recommended, especially for gated model access)

Hardware recommendations:
- **Minimum**: 8GB RAM, CPU only (slower responses)
- **Recommended**: CUDA-capable GPU
- **Optimal**: 12GB+ VRAM for smoother larger-model inference

---

## ⚙️ Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment

Create a `.env` file in the project root with V3 keys:

```env
HF_TOKEN=your_huggingface_token_here
BASE_MODEL_ID=Qwen/Qwen2.5-3B-Instruct
ADAPTER_MODEL_ID=your_finetuned_adapter_repo_or_leave_blank
MODEL_CACHE_DIR=.cache/models
USE_4BIT=true
MAX_INPUT_TOKENS=1200
MAX_NEW_TOKENS=140
```

Notes:
- `ADAPTER_MODEL_ID` is optional. Leave it blank to run base model only.
- If your `.env.example` contains older keys, prefer the keys above because they match the current V3 code.

### 3. Run the app

```bash
streamlit run App.py
```

Default URL: `http://localhost:8501`

---

## 🧪 Fine-tuning

Fine-tuning experiments are documented in:

```text
notebook/Nutrition Assist Finetune Notebook.ipynb
```

Typical workflow:

* prepare nutrition Q&A style examples
* train a LoRA adapter on top of the base model
* publish or save the adapter
* load it at runtime using `ADAPTER_MODEL_ID`

---

## 📊 Dataset

The grounding dataset is:

```text
data/nutrients.csv
```

The app uses it to inject factual values such as calories, protein, fat, fiber, and carbs into generation context.

---

## ⚡ Performance

This project runs a local model, so hardware matters.

* On lower GPUs or CPU, startup and responses may take longer
* On stronger GPUs, responses are faster and smoother

Current optimization choices:

* local model caching via Hugging Face snapshot download
* optional 4-bit quantization when CUDA is available
* short conversation history window
* lightweight dataset retrieval before generation
* optional adapter-based fine-tuned inference

---

## 🛠️ Troubleshooting

### Model download fails
- Verify `HF_TOKEN`
- Confirm model/adaptor access on Hugging Face

### Adapter fails to load
- Verify `ADAPTER_MODEL_ID` points to a valid PEFT adapter repository
- Leave `ADAPTER_MODEL_ID` blank to test base-model-only mode

### Missing PEFT package
- If you see `ModuleNotFoundError: peft`, install it with:

```bash
pip install peft
```

### Out of memory (OOM)
- Keep `USE_4BIT=true`
- Reduce `MAX_INPUT_TOKENS` and `MAX_NEW_TOKENS`
- Use a smaller base model

### Slow responses
- Expected on CPU for larger models
- Use a CUDA-enabled GPU or smaller model

### Port already in use

```bash
streamlit run App.py --server.port 8502
```

---

## 📂 Project Structure

```text
NutriAssist-AI/
|
|-- App.py
|-- requirements.txt
|-- README.md
|-- README_v3.md
|-- .env.example
|-- assets/
|   |-- Demo.png
|-- data/
|   |-- nutrients.csv
|-- modules/
|   |-- ai_router.py
|   |-- llama_handler.py
|   |-- nutrition_lookup.py
|-- notebook/
|   |-- Nutrition Assist Finetune Notebook.ipynb
```

---

## 🎯 Current Focus

* Improve nutrition response quality through fine-tuned behavior
* Combine dataset grounding with conversational usefulness
* Keep architecture simple and extensible for future product features

---

## 🔮 Future Enhancements

* Meal tracking and nutrition analysis workflows
* Food image understanding features
* User-aware conversational memory
* Faster and richer UI interactions

---

## 👨‍💻 Author

Developed by **Chinmay Bitne**

---

## 📄 License

This project is licensed under the MIT License.

For the base model (Qwen2.5-3B-Instruct), refer to: [Qwen License](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct)