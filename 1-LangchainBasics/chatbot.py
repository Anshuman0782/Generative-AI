import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os

# ── Environment ───────────────────────────────────────────────────────────────
load_dotenv()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Groq AI Chatbot", page_icon="🤖", layout="wide")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Settings")
    st.markdown("---")

    st.subheader("🧠 Choose Model")
    selected_model = st.selectbox(
        label="Groq Model",
        options=["llama-3.1-8b-instant", "gemma2-9b-it"],
        help="Select the LLM to power your chat session.",
    )

    st.markdown("---")

    st.subheader("📋 System Prompt")
    system_prompt = st.text_area(
        label="Instruction for the AI",
        value="You are a helpful, friendly, and concise AI assistant.",
        height=120,
    )

    st.markdown("---")

    st.subheader("ℹ️ Model Info")
    model_info = {
        "llama-3.1-8b-instant": {"Provider": "Meta",   "Parameters": "8B", "Strength": "Ultra-fast"},
        "gemma2-9b-it":         {"Provider": "Google", "Parameters": "9B", "Strength": "Instruction-tuned"},
    }
    for key, val in model_info[selected_model].items():
        st.write(f"**{key}:** {val}")

    st.markdown("---")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ── Main area ─────────────────────────────────────────────────────────────────
st.title("🤖 AI Chatbot")
st.caption(f"Powered by **{selected_model}** via Groq  ·  Built with LangChain & Streamlit")
st.markdown("---")

if not GROQ_API_KEY:
    st.error("❌ **GROQ_API_KEY not found.** Add it to your `.env` file.")
    st.stop()

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── LangChain chain ───────────────────────────────────────────────────────────
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "{system_prompt}"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{user_input}"),
])

llm = ChatGroq(
    model=selected_model,
    api_key=GROQ_API_KEY,
    temperature=0.7,
    streaming=True,
)

chain = prompt_template | llm | StrOutputParser()

# ── Render chat history ───────────────────────────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ── User input ────────────────────────────────────────────────────────────────
user_input = st.chat_input("Type your message here…")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    chat_history = []
    for msg in st.session_state.messages[:-1]:
        if msg["role"] == "user":
            chat_history.append(HumanMessage(content=msg["content"]))
        else:
            chat_history.append(AIMessage(content=msg["content"]))

    with st.chat_message("assistant"):
        response = st.write_stream(
            chain.stream({
                "system_prompt": system_prompt,
                "chat_history": chat_history,
                "user_input": user_input,
            })
        )

    st.session_state.messages.append({"role": "assistant", "content": response})

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:gray; font-size:0.8rem;'>"
    "Built with ❤️ using Streamlit · LangChain · Groq"
    "</div>",
    unsafe_allow_html=True,
)