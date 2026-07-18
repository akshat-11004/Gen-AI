import os
from dotenv import load_dotenv
import streamlit as st
from langchain_groq import ChatGroq
# 1. Import modern, fast agent structures
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_community.tools import DuckDuckGoSearchRun, WikipediaQueryRun, ArxivQueryRun
from langchain_community.utilities import WikipediaAPIWrapper, ArxivAPIWrapper
from langchain_classic.callbacks import StreamlitCallbackHandler
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

load_dotenv()

if os.getenv("LANGCHAIN_API_KEY"):
    os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = "Search Engine"

# --------------------------------------------------
# Page Config
# --------------------------------------------------
st.set_page_config(
    page_title="AI Search Assistant",
    page_icon="🔎",
    layout="wide"
)

st.title("🔎 AI Search Assistant")
st.markdown(
    "Search the **Web**, **Wikipedia**, and **Arxiv** using **Groq + LangChain**."
)

# --------------------------------------------------
# Sidebar
# --------------------------------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input(
        "Groq API Key",
        type="password"
    )

# --------------------------------------------------
# Check API Key
# --------------------------------------------------
if not api_key:
    st.info("Please enter your Groq API Key in the sidebar.")
    st.stop()

# --------------------------------------------------
# Cache Agent (Upgraded for maximum speed)
# --------------------------------------------------
@st.cache_resource
def load_agent(groq_api_key):
    # Instantiating tools inside cache block limits latency issues
    arxiv = ArxivQueryRun(
        api_wrapper=ArxivAPIWrapper(
            top_k_results=1,
            doc_content_chars_max=300
        )
    )

    wiki = WikipediaQueryRun(
        api_wrapper=WikipediaAPIWrapper(
            top_k_results=1,
            doc_content_chars_max=300
        )
    )

    search = DuckDuckGoSearchRun()
    tools = [arxiv, search, wiki]

    # Llama 3.1 8B Instant handles native tool-calling incredibly quickly
    llm = ChatGroq(
        groq_api_key=groq_api_key,
        model_name="llama-3.1-8b-instant",
        streaming=True,
        temperature=0.2 # Slight temperature prevents reasoning deadlocks
    )

    # Clean, modern system template designed specifically for high-speed tool calls
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a fast, concise AI search assistant. Use tools only when you lack specific info or dates."),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # Build the lightning-fast modern tool agent
    agent = create_tool_calling_agent(llm, tools, prompt)
    
    # Configure strict execution boundaries so it never loops forever
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True,
        # max_iterations=2, # Prevents long thinking delays if tools don't match
        handle_parsing_errors=True
    )

    return agent_executor

agent_executor = load_agent(api_key)

# --------------------------------------------------
# Chat History
# --------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "👋 Hi! I'm your AI Search Assistant.\n\nAsk me anything!"
        }
    ]

for message in st.session_state.messages:
    with st.chat_message(
        message["role"],
        avatar="🤖" if message["role"] == "assistant" else "🧑",
    ):
        st.markdown(message["content"])

# --------------------------------------------------
# Chat Input & Invocation
# --------------------------------------------------
prompt = st.chat_input("Ask me anything...")

if prompt:
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        st_cb = StreamlitCallbackHandler(
            st.container(),
            expand_new_thoughts=False
        )

        with st.spinner("Searching..."):
            # Execute modern invoke architecture
            result_dict = agent_executor.invoke(
                {"input": prompt}, 
                config={"callbacks": [st_cb]}
            )
            # Pull directly from output node
            response_text = result_dict.get("output", "No response generated.")

        st.markdown(response_text)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response_text,
        }
    )
