import streamlit as st
from dotenv import load_dotenv
import os

from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load environment variables
load_dotenv()

# LangSmith (Optional)
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Simple Q&A Chatbot With Ollama"

# Prompt Template
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant. Please respond to the user's queries."
        ),
        ("user", "Question: {question}")
    ]
)


def generate_response(question, model_name, temperature, max_tokens):
    llm = OllamaLLM(
        model=model_name,
        temperature=temperature,
        num_predict=max_tokens
    )

    chain = prompt | llm | StrOutputParser()

    return chain.invoke({"question": question})


# Streamlit UI
st.title("Enhanced Q&A Chatbot With Ollama")

# Sidebar
model_name = st.sidebar.selectbox(
    "Select Model",
    ["llama3", "gemma:2b"]
)

temperature = st.sidebar.slider(
    "Temperature",
    min_value=0.0,
    max_value=1.0,
    value=0.7
)

max_tokens = st.sidebar.slider(
    "Max Tokens",
    min_value=50,
    max_value=500,
    value=150
)

# Main UI
st.write("Ask me anything!")

user_input = st.text_input("You:")

if st.button("Generate"):
    if user_input.strip():
        with st.spinner("Generating response..."):
            response = generate_response(
                user_input,
                model_name,
                temperature,
                max_tokens
            )

        st.success("Response")
        st.write(response)
    else:
        st.warning("Please enter a question.")