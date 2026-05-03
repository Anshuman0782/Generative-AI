# 🤖 Groq AI Chatbot

A conversational AI chatbot built with **Streamlit**, **LangChain**, and **Groq** — featuring model selection, customizable system prompts, multi-turn memory, and streaming responses.

---

## 📸 Features

- 🧠 Choose between **2 Groq models** (Llama 3.1 & Gemma 2)
- 💬 **Multi-turn conversation** with full chat memory
- ⚡ **Streaming responses** — tokens appear in real time
- 📋 **Custom system prompt** — change the AI's personality from the sidebar
- 🗑️ **Clear Chat button** — reset the conversation instantly
- 🔐 **Secure API key loading** via `.env` file

---

## 🗂️ Project Structure

```
project/
├── chatbot.py        # Main application file
├── .env              # Your secret API key (never commit this)
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

---

## ⚙️ Tech Stack

| Library | Purpose |
|---|---|
| `streamlit` | Builds the browser-based UI without any HTML/JS |
| `langchain-groq` | LangChain's connector to Groq's inference API |
| `langchain-core` | Core LangChain primitives: prompts, messages, parsers |
| `python-dotenv` | Loads `GROQ_API_KEY` from the `.env` file securely |

---

## 🚀 Getting Started

### 1. Clone or download the project

```bash
git clone <your-repo-url>
cd project
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install streamlit langchain langchain-groq langchain-core python-dotenv
```

Or if you have a `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 4. Set up your `.env` file

Your `.env` file already has the key. Make sure it looks like this:

```env
GROQ_API_KEY=your_actual_groq_api_key_here
```

> ⚠️ Never commit the `.env` file to Git. Add it to `.gitignore`.

### 5. Run the app

```bash
streamlit run chatbot.py
```

The app will open automatically at `http://localhost:8501`.

---

## 🧩 Code Explained

### Imports & Environment

```python
load_dotenv()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
```

`load_dotenv()` reads the `.env` file and injects all key-value pairs into `os.environ`. This keeps secrets out of source code.

---

### Sidebar

The sidebar has three sections:

| Section | What it does |
|---|---|
| **Choose Model** | `st.selectbox` lets the user switch between the two Groq models |
| **System Prompt** | `st.text_area` lets the user customize the AI's behavior/persona |
| **Clear Chat** | `st.button` wipes `st.session_state.messages` and calls `st.rerun()` |

---

### Session State

```python
if "messages" not in st.session_state:
    st.session_state.messages = []
```

Streamlit **re-runs the entire script** on every user interaction. `st.session_state` is a persistent dictionary that survives these re-runs within the same browser session. We store all chat messages here as a list of `{"role": ..., "content": ...}` dicts.

---

### LangChain Chain

```python
chain = prompt_template | llm | StrOutputParser()
```

The `|` operator is **LCEL (LangChain Expression Language)** — it chains components so the output of one feeds into the next.

**The pipeline:**

```
ChatPromptTemplate → ChatGroq (LLM) → StrOutputParser
```

#### ChatPromptTemplate

```python
ChatPromptTemplate.from_messages([
    ("system", "{system_prompt}"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{user_input}"),
])
```

| Slot | Description |
|---|---|
| `system` | Hidden instruction that shapes the AI's personality |
| `MessagesPlaceholder` | Inserts the full conversation history — this gives the model **memory** |
| `human` | The current user message |

#### ChatGroq

```python
llm = ChatGroq(model=selected_model, api_key=GROQ_API_KEY, temperature=0.7, streaming=True)
```

| Parameter | Description |
|---|---|
| `model` | The Groq model ID selected from the sidebar |
| `api_key` | Your Groq API key loaded from `.env` |
| `temperature` | Randomness: `0.0` = factual, `1.0` = creative, `0.7` = balanced |
| `streaming` | `True` enables token-by-token streaming for the typewriter effect |

#### StrOutputParser

Converts LangChain's `AIMessage` object → plain Python `str`.

---

### Chat History → LangChain Messages

```python
for msg in st.session_state.messages[:-1]:
    if msg["role"] == "user":
        chat_history.append(HumanMessage(content=msg["content"]))
    else:
        chat_history.append(AIMessage(content=msg["content"]))
```

The chain's `MessagesPlaceholder` expects `HumanMessage` / `AIMessage` objects (not plain dicts), so we convert the history before each API call. We skip the latest message because it's passed separately as `user_input`.

---

### Streaming Response

```python
response = st.write_stream(chain.stream({...}))
```

`chain.stream()` returns a **generator** that yields string fragments as the model produces them. `st.write_stream()` consumes the generator and renders each chunk live in the UI — creating the typewriter effect.

---

## 🤖 Available Models

### `llama-3.1-8b-instant`
- **Provider:** Meta
- **Parameters:** 8 Billion
- **Best for:** Fast, everyday conversations and general Q&A
- **Strength:** Extremely low latency on Groq hardware

### `gemma2-9b-it`
- **Provider:** Google
- **Parameters:** 9 Billion
- **Best for:** Following complex instructions, structured tasks
- **Strength:** Strong instruction-following capability

---

## 🔑 Getting a Groq API Key

1. Go to [https://console.groq.com](https://console.groq.com)
2. Sign up or log in
3. Navigate to **API Keys** → **Create API Key**
4. Copy the key and paste it into your `.env` file

---

## 📦 requirements.txt

```
streamlit
langchain
langchain-groq
langchain-core
python-dotenv
```

---

## 🛡️ Security Notes

- Never hardcode your API key in `chatbot.py`
- Add `.env` to your `.gitignore` before pushing to GitHub:

```gitignore
.env
__pycache__/
*.pyc
```

---

## 📄 License

MIT — free to use, modify, and distribute.