# 🤖 Groq AI Chatbot + LangChain Tools

A two-part project covering:
1. **`chatbot.py`** — A fully functional Streamlit chatbot powered by Groq & LangChain
2. **`tools.ipynb`** — A hands-on notebook exploring LangChain Tools (custom, structured, and built-in)

---

## 📁 Project Structure

```
project/
├── chatbot.py        # Streamlit chatbot application
├── tools.ipynb       # LangChain Tools tutorial notebook
├── .env              # Secret API keys (never commit this)
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

---

## ⚙️ Tech Stack

| Library | Used In | Purpose |
|---|---|---|
| `streamlit` | chatbot.py | Browser-based UI without HTML/JS |
| `langchain-groq` | both | LangChain connector to Groq's inference API |
| `langchain-core` | both | Core primitives: prompts, messages, parsers, tools |
| `langchain-community` | tools.ipynb | Community integrations (Wikipedia, etc.) |
| `python-dotenv` | chatbot.py | Loads API keys from `.env` securely |

---

## 🚀 Getting Started

### 1. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### 2. Install dependencies

```bash
pip install streamlit langchain langchain-groq langchain-core langchain-community python-dotenv wikipedia
```

### 3. Set up your `.env` file

```env
GROQ_API_KEY=your_actual_groq_api_key_here
```

> ⚠️ Never commit `.env` to Git. Add it to `.gitignore`.

### 4. Get a Groq API Key

1. Visit [https://console.groq.com](https://console.groq.com)
2. Sign up / Log in → **API Keys** → **Create API Key**
3. Paste it into `.env`

---

---

# 📄 File 1 — `chatbot.py`

A conversational AI chatbot with a sidebar, streaming responses, and multi-turn memory.

## ▶️ Run the App

```bash
streamlit run chatbot.py
```

Opens automatically at `http://localhost:8501`

## ✨ Features

- 🧠 Switch between **2 Groq models** from the sidebar
- 💬 **Multi-turn memory** — the AI remembers earlier messages
- ⚡ **Streaming responses** — tokens appear in real time (typewriter effect)
- 📋 **Custom system prompt** — change the AI's persona on the fly
- 🗑️ **Clear Chat button** — reset the conversation instantly
- 🔐 API key loaded securely from `.env`

## 🖥️ UI Layout

```
┌─────────────────┬────────────────────────────────────┐
│   SIDEBAR       │         MAIN CHAT AREA              │
│                 │                                     │
│  ⚙️ Settings    │  🤖 AI Chatbot                     │
│  ─────────────  │  ─────────────────────────────────  │
│  🧠 Model       │  [user message bubble]              │
│  selectbox      │  [assistant reply bubble]           │
│                 │  [user message bubble]              │
│  📋 System      │  [assistant reply bubble]           │
│  Prompt         │                                     │
│  text area      │                                     │
│                 │                                     │
│  ℹ️ Model Info  │                                     │
│                 │  ─────────────────────────────────  │
│  🗑️ Clear Chat  │  [ Type your message here…     ↵ ] │
└─────────────────┴────────────────────────────────────┘
```

## 🧩 Code Breakdown

### Environment Setup

```python
load_dotenv()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
```

`load_dotenv()` reads `.env` and injects values into `os.environ`. Keeps secrets out of code.

---

### Session State (Chat Memory)

```python
if "messages" not in st.session_state:
    st.session_state.messages = []
```

Streamlit **re-runs the entire script** on every interaction. `st.session_state` is a persistent dictionary that survives these re-runs, so the chat history is never lost mid-conversation.

Each message is stored as:
```python
{"role": "user" | "assistant", "content": "message text"}
```

---

### Clear Chat Button

```python
if st.button("🗑️ Clear Chat", use_container_width=True):
    st.session_state.messages = []
    st.rerun()
```

Wipes the message list and calls `st.rerun()` to force an immediate refresh, clearing the screen instantly.

---

### LangChain Chain (LCEL Pipeline)

```python
chain = prompt_template | llm | StrOutputParser()
```

The `|` pipe operator is **LCEL (LangChain Expression Language)**. It connects components so each one's output feeds the next.

**Pipeline flow:**
```
ChatPromptTemplate  →  ChatGroq  →  StrOutputParser
      ↓                    ↓               ↓
 Fills slots           Calls Groq      Returns plain
 with history,         API & streams   Python string
 system prompt,        response
 user input
```

#### ChatPromptTemplate — The 3 Slots

```python
ChatPromptTemplate.from_messages([
    ("system", "{system_prompt}"),                          # AI persona
    MessagesPlaceholder(variable_name="chat_history"),      # conversation memory
    ("human", "{user_input}"),                              # current message
])
```

| Slot | Description |
|---|---|
| `system` | Hidden instruction for the AI's behaviour/personality |
| `MessagesPlaceholder` | Injects the entire conversation history — gives the model **memory** |
| `human` | The current user message, appended just before each API call |

#### ChatGroq — The LLM

```python
llm = ChatGroq(model=selected_model, api_key=GROQ_API_KEY, temperature=0.7, streaming=True)
```

| Parameter | Description |
|---|---|
| `model` | The Groq model ID selected in the sidebar |
| `api_key` | Key loaded from `.env` |
| `temperature` | `0.0` = factual/deterministic · `1.0` = creative · `0.7` = balanced |
| `streaming=True` | Yields tokens as they are generated (enables typewriter effect) |

#### StrOutputParser

Converts LangChain's `AIMessage` wrapper object → plain Python `str`.

---

### Converting History to LangChain Messages

```python
for msg in st.session_state.messages[:-1]:
    if msg["role"] == "user":
        chat_history.append(HumanMessage(content=msg["content"]))
    else:
        chat_history.append(AIMessage(content=msg["content"]))
```

The chain's `MessagesPlaceholder` requires `HumanMessage` / `AIMessage` objects — not plain dicts — so we convert before every API call. The latest message is excluded here because it's already passed separately as `user_input`.

---

### Streaming the Response

```python
response = st.write_stream(chain.stream({...}))
```

`chain.stream()` returns a **generator** that yields string fragments as Groq produces them. `st.write_stream()` renders each fragment live, producing the typewriter effect. It also returns the full concatenated string when done.

---

## 🤖 Available Models

### `llama-3.1-8b-instant`
- **Provider:** Meta · **Parameters:** 8 Billion
- **Best for:** Fast everyday conversations, general Q&A
- **Strength:** Extremely low latency on Groq's LPU hardware

### `gemma2-9b-it`
- **Provider:** Google · **Parameters:** 9 Billion
- **Best for:** Complex instructions, structured tasks
- **Strength:** Strong instruction-following capability

---

---

# 📓 File 2 — `tools.ipynb`

A hands-on notebook covering **LangChain Tools** — how to create, configure, and use tools with LLMs.

## Topics Covered

1. How to create custom tools
2. How to use built-in tools and toolkits
3. How to connect tools to a chat model
4. How to pass tool outputs back to the model

---

## 🔧 1. Creating Custom Tools with `@tool`

The `@tool` decorator is the simplest way to define a custom tool. The function name becomes the tool name and the **docstring becomes the tool's description** (required).

```python
from langchain_core.tools import tool

@tool
def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b
```

You can also use `Annotated` to add descriptions to each parameter:

```python
from typing import Annotated, List

@tool
def multiply_by_max(
    a: Annotated[float, "First number"],
    b: Annotated[List[float], "List of numbers"]
) -> float:
    """Multiply a by the maximum value in b."""
    return a * max(b)
```

---

## 🏗️ 2. Structured Tools (`StructuredTool`)

A `StructuredTool` uses a defined input schema instead of plain text. It tells the AI exactly what inputs are required, their types, and how to call the function.

```python
from langchain_core.tools import StructuredTool

def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b

async def amultiply(a: float, b: float) -> float:
    """Multiply two numbers (async)."""
    return a * b

calculate = StructuredTool.from_function(func=multiply, coroutine=amultiply)

print(calculate.invoke({"a": 5, "b": 10}))         # sync call → 50
print(await calculate.ainvoke({"a": 5, "b": 5}))   # async call → 25
```

| Feature | `@tool` | `StructuredTool` |
|---|---|---|
| Ease of use | ✅ Very simple | Slightly more setup |
| Async support | Manual | Built-in via `coroutine=` |
| Schema control | Via type hints | Full Pydantic schema |

---

## 🌐 3. Built-in Tools — Wikipedia

LangChain Community provides ready-made tools. Wikipedia is a common one:

```python
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

api_wrapper = WikipediaAPIWrapper(top_k_results=5, doc_content_chars_max=500)
wiki_tool = WikipediaQueryRun(api_wrapper=api_wrapper)

print(wiki_tool.invoke({"query": "What is the capital of India?"}))
```

| Parameter | Description |
|---|---|
| `top_k_results` | Number of Wikipedia articles to retrieve |
| `doc_content_chars_max` | Max characters returned per article |

---

## 🤝 4. Binding Tools to an LLM

Tools are bound to the model with `.bind_tools()`. The model then decides which tool to call based on the user's query.

```python
from langchain.chat_models import init_chat_model

llm = init_chat_model("qwen/qwen3-32b", model_provider="groq")

tools = [wiki_tool, add, multiply]
llm_with_tools = llm.bind_tools(tools)
```

---

## 🔄 5. Full Tool-Calling Flow

```python
from langchain_core.messages import HumanMessage

query = "What is 2*3 and what is the capital of India?"
messages = [HumanMessage(query)]

# Step 1: LLM decides which tools to call
response = llm_with_tools.invoke(query)
print(response.tool_calls)
# → [{"name": "multiply", "args": {"a": 2, "b": 3}}, {"name": "wikipedia", ...}]

# Step 2: Execute each tool and collect results
tool_map = {"add": add, "multiply": multiply, "wikipedia": wiki_tool}
for tool_call in response.tool_calls:
    selected_tool = tool_map[tool_call["name"].lower()]
    tool_msg = selected_tool.invoke(tool_call)
    messages.append(tool_msg)

# Step 3: Send tool results back to the LLM for a final answer
final_response = llm_with_tools.invoke(messages)
```

**Flow diagram:**
```
User query
    ↓
LLM decides which tools to call  (response.tool_calls)
    ↓
Tools are executed                (selected_tool.invoke)
    ↓
Results appended to messages
    ↓
LLM generates final answer        (llm_with_tools.invoke(messages))
```

---

---

## 🛡️ Security Notes

- Never hardcode API keys in `.py` or `.ipynb` files
- Add `.env` to `.gitignore`:

```gitignore
.env
__pycache__/
*.pyc
.ipynb_checkpoints/
```

---

## 📦 `requirements.txt`

```
streamlit
langchain
langchain-groq
langchain-core
langchain-community
python-dotenv
wikipedia
```

---

## 📄 License

MIT — free to use, modify, and distribute.

---

*Built with ❤️ by Anshuman | Powered by Groq AI | Made with Streamlit & LangChain*