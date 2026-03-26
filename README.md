# 🥗 NutriAssist AI

![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-Latest-red) ![License](https://img.shields.io/badge/License-MIT-green)

NutriAssist AI is an intelligent nutrition assistant that helps users understand food, diet, and healthy eating through natural conversation.

It provides a clean and responsive chat interface powered by a locally running language model, enabling users to ask questions about nutrition, calories, and healthy habits.

---

##  Overview

NutriAssist AI allows users to:

* 💬 Ask nutrition-related questions in natural language
* 🤖 Get AI-generated responses using a local language model
* ⚡ Run fully on local hardware (no dependency on external APIs)
* 🎯 Interact through a simple and intuitive chat interface

This project is designed to be a foundation for building a complete AI-powered nutrition system.

---

## 🧠 How It Works

The system follows a simple pipeline:

```text
User Input → Streamlit UI → AI Router → Language Model → Response → UI
```

### Flow:

1. User enters a nutrition-related query
2. Input is processed and routed to the model
3. Model generates a response
4. Response is displayed in chat format

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

  * Routes user queries to the model

* **LLM Handler**

  * Loads and runs the local language model
  * Handles prompt formatting and generation

---

## ✅ Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8 or higher**
- **pip** (Python package manager)
- **Git** (optional, for cloning the repository)
- **HuggingFace Account** (for downloading the base model)

Hardware recommendations:
- **Minimum**: 8GB RAM, CPU only (slower response times)
- **Recommended**: GPU with CUDA support (for faster inference)
- **Optimal**: 12GB+ VRAM GPU (NVIDIA RTX series or better)

---

## ⚙️ Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 2. Configure environment

Create a `.env` file in the project root (you can copy from `.env.example`):

```env
HF_TOKEN=your_huggingface_token_here
BASE_MODEL_ID=Qwen/Qwen2.5-3B-Instruct
MODEL_CACHE_DIR=.cache/models
USE_4BIT=true
MAX_INPUT_TOKENS=1024
MAX_NEW_TOKENS=120
```

**Configuration Options:**
- `HF_TOKEN`: Your HuggingFace API token (get it from [huggingface.co](https://huggingface.co/settings/tokens))
- `BASE_MODEL_ID`: Model identifier from HuggingFace Hub
- `MODEL_CACHE_DIR`: Directory for cached model files
- `USE_4BIT`: Enable 4-bit quantization for reduced memory usage
- `MAX_INPUT_TOKENS`: Maximum input length for the model
- `MAX_NEW_TOKENS`: Maximum tokens to generate in response

---

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

# 2. Set up environment variables
# Copy .env.example to .env and fill in your HF_TOKEN

# 3. Run the application
streamlit run App.py

# Your nutrition assistant is now ready! 🎉
```

---

## ⚡ Performance

This project runs a local language model.

- On **lower GPUs or CPU**, startup and replies may take longer
- On **stronger GPUs**, loading and generation become much faster and smoother

The app is optimized with:
- local model caching
- optional 4-bit loading
- short conversation history
- lightweight dataset lookup before generation

---

## � Troubleshooting

### Model Loading Issues
- **Issue**: The model fails to download from HuggingFace
- **Solution**: Ensure your `HF_TOKEN` is valid and that you have accepted the model's license on HuggingFace

### Out of Memory (OOM) Errors
- **Issue**: CUDA out of memory or RAM exhausted
- **Solution**: Enable 4-bit loading in `.env` (`USE_4BIT=true`), reduce `MAX_INPUT_TOKENS` or `MAX_NEW_TOKENS`

### Slow Response Times
- **Issue**: Taking too long to generate responses
- **Solution**: Consider using a smaller model, enable quantization, or upgrade to a GPU

### Port Already in Use
- **Issue**: Streamlit fails to start with port in use error
- **Solution**: Run `streamlit run App.py --server.port 8502` to use a different port

### Import Errors
- **Issue**: `ModuleNotFoundError` when running the app
- **Solution**: Reinstall requirements with `pip install -r requirements.txt --upgrade`

---

## �📂 Project Structure

```
NutriAssist-AI/
│
├── App.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env.example
│
└── modules/
    ├── ai_router.py
    └── llama_handler.py
```

---

## 🎯 Design Goals

* Build a clean and simple AI chatbot interface
* Enable local model inference without external dependencies
* Keep the system modular and extensible
* Ensure compatibility across different hardware setups

---

## 🔮 Future Enhancements

The system is designed to evolve with additional capabilities such as:

* 📊 Nutrition dataset integration
* 🧠 Personalized user context
* 🍽️ Meal tracking system
* 📸 Food image detection
* ⚡ Performance optimization

---

## 👨‍💻 Author

Developed by **Chinmay Bitne**

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

For the base model (Qwen2.5-3B-Instruct), please refer to the [Qwen License](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct)
