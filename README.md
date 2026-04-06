# 🥗 NutriAssist AI

![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-Latest-red) ![License](https://img.shields.io/badge/License-MIT-green)

NutriAssist AI is an intelligent nutrition assistant that helps users understand food, diet, and healthy eating through natural conversation.

It provides a clean and responsive chat interface powered by a locally running language model.

Version 2 extends the original project with dataset-grounded food facts, so answers are both conversational and more reliable.

---

## 📌 Overview

NutriAssist AI allows users to:

* 💬 Ask nutrition-related questions in natural language
* 🤖 Get AI-generated responses using a local language model
* 📊 Use nutrition dataset context for grounded food answers
* ⚡ Run fully on local hardware (no paid external API required)
* 🎯 Interact through a simple and intuitive chat interface

This project is designed as a practical foundation for building a complete AI-powered nutrition system.

---

## 🆕 What's New in V2

Compared to V1, this release adds:

* Nutrition lookup from `data/nutrients.csv`
* Exact and fuzzy food matching in `modules/nutrition_lookup.py`
* Automatic context injection into the model prompt
* Better defaults for local inference on both CPU and GPU


---

## 🧠 How It Works

The system follows this pipeline:

```text
User Input -> Streamlit UI -> AI Router -> Nutrition Lookup -> Language Model -> Response -> UI
```

### Flow

1. User enters a nutrition-related query
2. Input is routed to the AI handler
3. System searches the nutrition dataset for relevant food matches
4. Model generates a final response using dataset context + conversation history
5. Response is displayed in chat format

---

## 📸 Demo

![Demo](assets/Demo.png)

---

## 🏗️ Architecture

### Components

* **Streamlit UI**
  * Handles chat interface
  * Displays conversation history

* **AI Router**
  * Routes user queries to the model layer

* **Nutrition Lookup**
  * Reads and searches `nutrients.csv`
  * Builds structured nutrition facts context

* **LLM Handler**
  * Downloads/caches model locally
  * Formats prompt and generates final response

---

## ✅ Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10 or higher**
- **pip** (Python package manager)
- **Git** (optional, for cloning the repository)
- **Hugging Face account** (for model download/access)

Hardware recommendations:
- **Minimum**: 8GB RAM, CPU only (slower response times)
- **Recommended**: GPU with CUDA support (faster inference)
- **Optimal**: 12GB+ VRAM GPU (NVIDIA RTX series or better)

---

## ⚙️ Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 2. Configure environment

Create a `.env` file in the project root:

```env
HF_TOKEN=your_huggingface_token_here
BASE_MODEL_ID=Qwen/Qwen2.5-3B-Instruct
MODEL_CACHE_DIR=.cache/models
USE_4BIT=true
MAX_INPUT_TOKENS=1200
MAX_NEW_TOKENS=140
```

### 3. Run the application

```bash
streamlit run App.py
```

The app will open in your default browser at `http://localhost:8501`

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env with required variables

# 3. Run the app
streamlit run App.py
```

---

## ⚡ Performance

This project runs a local language model.

- On **CPU or lower GPUs**, startup and replies may take longer
- On **stronger GPUs**, loading and generation are much faster

The app is optimized with:
- local model caching
- optional 4-bit loading
- short conversation history window
- lightweight dataset lookup before generation

---

## 🛠️ Troubleshooting

### Model Loading Issues
- **Issue**: The model fails to download from Hugging Face
- **Solution**: Ensure your `HF_TOKEN` is valid and model access is enabled

### Out of Memory (OOM) Errors
- **Issue**: CUDA out of memory or RAM exhausted
- **Solution**: Keep `USE_4BIT=true`, reduce `MAX_INPUT_TOKENS` and `MAX_NEW_TOKENS`, or use a smaller model

### Slow Response Times
- **Issue**: Generation is too slow
- **Solution**: Use a smaller model, enable quantization, or use a CUDA-enabled GPU

### Port Already in Use
- **Issue**: Streamlit fails to start with port in use error
- **Solution**:

```bash
streamlit run App.py --server.port 8502
```

### Import Errors
- **Issue**: `ModuleNotFoundError` when running the app
- **Solution**: Reinstall dependencies using:

```bash
pip install -r requirements.txt --upgrade
```

---

## 📂 Project Structure

```text
NutriAssist-AI/
|
|-- App.py
|-- requirements.txt
|-- README.md
|-- .gitignore
|-- .env.example
|-- assets/
|   |-- Demo.png
|-- data/
|   |-- nutrients.csv
|-- modules/
|   |-- ai_router.py
|   |-- llama_handler.py
|   |-- nutrition_lookup.py
```

---

## 🎯 Design Goals

* Build a clean and simple AI chatbot interface
* Enable local model inference without mandatory external APIs
* Keep the system modular and extensible
* Provide more grounded food answers with dataset support
* Ensure compatibility across different hardware setups

---

## 🔮 Future Enhancements

The system is designed to evolve with additional capabilities such as:

* 📊 Better dataset normalization and validation
* 🧠 Personalized user context and goals
* 🍽️ Meal planning and tracking workflows
* 📱 Richer UI cards for nutrient summaries
* ⚡ Faster inference and caching improvements

---

## 👨‍💻 Author

Developed by **Chinmay Bitne**

---

## 📄 License

This project is licensed under the MIT License.

For the base model (Qwen2.5-3B-Instruct), please refer to the [Qwen License](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct)