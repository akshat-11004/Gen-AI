import os
from dotenv import load_dotenv
import streamlit as st
from langchain_ollama import OllamaLLM as Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Page config must be first
st.set_page_config(page_title="AI Engineer Assistant", page_icon="🤖", layout="wide")

load_dotenv()

# Langsmith Tracking
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")

# Custom CSS for a cleaner look
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stTextInput {
        transition: all 0.3s ease-in-out;
    }
    .stTextInput:focus-within {
        transform: scale(1.01);
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar for settings
with st.sidebar:
    st.title("⚙️ Settings")
    st.info("Using Opensource Models via Ollama local runtime.")
    model_name = st.selectbox("Select Model", ["llama3", "gemma:2b"], index=0)
    st.divider()
    st.caption("Developed by Expert AI Engineer")

# Main UI Header
st.title("🤖 Use OpenSource Ollama")
st.markdown("---")

# Layout columns
col1, col2 = st.columns(2)

with col1:
    input_text = st.text_input("Ask me anything about AI or Engineering:", placeholder="e.g., How do I optimize a RAG pipeline?")

# Prompt Template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert AI engineer. Please provide concise, high-quality technical responses."),
    ("user", "Question: {question}")
])

# Chain Setup
llm = Ollama(model=model_name)
output_parser = StrOutputParser()
chain = prompt | llm | output_parser

# Response Handling
if input_text:
    with st.spinner('🧠 Thinking...'):
        try:
            response = chain.invoke({"question": input_text})
            
            # Beautiful Response Container
            with st.container():
                st.subheader("🚀 Analysis")
                st.markdown(response)
        except Exception as e:
            st.error(f"Error: {str(e)}")
else:
    st.info("👋 Welcome! Please enter a question to start the interaction.")
