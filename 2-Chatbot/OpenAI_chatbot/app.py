import streamlit as st
import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load environment variables
load_dotenv()

# LangSmith Tracking (Optional)
if os.getenv("LANGCHAIN_API_KEY"):
    os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = "Simple Q&A Chatbot With OpenAI"

# Prompt Template
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant. Please respond to the user's queries."),
        ("user", "Question: {question}")
    ]
)

# Function to generate response
def generate_response(question, api_key, model, temperature, max_tokens):
    llm = ChatOpenAI(
        model=model,
        api_key=api_key,
        temperature=temperature,
        max_tokens=max_tokens
    )

    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser

    return chain.invoke({"question": question})

# Streamlit UI
st.title("Enhanced Q&A Chatbot with OpenAI")

# Sidebar
st.sidebar.title("Settings")

api_key = st.sidebar.text_input(
    "Enter your OpenAI API Key",
    type="password"
)

model = st.sidebar.selectbox(
    "Select OpenAI Model",
    [
        "gpt-5.5",
        "gpt-5.4",
        "gpt-5.4-mini"
    ]
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

# Main Interface
st.write("Go ahead and ask any question.")

user_input = st.text_input("You:")

if st.button("Ask"):
    if not api_key:
        st.warning("Please enter your OpenAI API key.")
    elif not user_input:
        st.warning("Please enter a question.")
    else:
        with st.spinner("Generating response..."):
            response = generate_response(
                user_input,
                api_key,
                model,
                temperature,
                max_tokens
            )
        st.success(response)