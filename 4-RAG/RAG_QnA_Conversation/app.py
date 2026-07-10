import os
import tempfile
from dotenv import load_dotenv
import streamlit as st

from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.chat_message_histories import ChatMessageHistory

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

from langchain_classic.chains import create_history_aware_retriever,create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain


load_dotenv()

# LangSmith Tracking (Optional)
if os.getenv("LANGCHAIN_API_KEY"):
    os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = "RAG_Q&A_Conversation"

st.set_page_config(page_title="Conversational PDF RAG", page_icon="📄", layout="wide")
st.title("📄 Conversational PDF RAG")
st.caption("Upload one or more PDFs and chat with them.")

@st.cache_resource
def load_embeddings():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

embeddings = load_embeddings()

if "store" not in st.session_state:
    st.session_state.store = {}
if "rag_chain" not in st.session_state:
    st.session_state.rag_chain = None
if "docs_loaded" not in st.session_state:
    st.session_state.docs_loaded = False

with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Groq API Key", type="password")
    session_id = st.text_input("Session ID", value="default")
    uploaded_files = st.file_uploader(
        "Upload PDFs",
        type="pdf",
        accept_multiple_files=True
    )

def get_session_history(session: str) -> BaseChatMessageHistory:
    if session not in st.session_state.store:
        st.session_state.store[session] = ChatMessageHistory()
    return st.session_state.store[session]

if api_key and uploaded_files and not st.session_state.docs_loaded:

    llm = ChatGroq(groq_api_key=api_key,model_name="llama-3.3-70b-versatile",)

    documents = []

    with st.spinner("Processing PDFs..."):
        for pdf in uploaded_files:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(pdf.getvalue())
                path = tmp.name

            loader = PyPDFLoader(path)
            documents.extend(loader.load())
            os.remove(path)

        splitter = RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=500)
        splits = splitter.split_documents(documents)

        vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)        

        retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

        contextualize_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "Given the chat history and latest user question, rewrite the "
                "question so it is standalone. Do not answer it."
            ),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ])

        history_aware_retriever = create_history_aware_retriever(llm,retriever,contextualize_prompt)

        qa_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """You are a helpful assistant for answering questions from uploaded PDFs.

                Use ONLY the retrieved context.

                If the answer is not present, say:
                'I couldn't find that information in the uploaded PDFs.'

                Keep answers concise.

                Context:
                {context}
                """
            ),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ])

        qa_chain = create_stuff_documents_chain(
            llm,
            qa_prompt
        )

        rag_chain = create_retrieval_chain(
            history_aware_retriever,
            qa_chain
        )

        st.session_state.rag_chain = RunnableWithMessageHistory(
            rag_chain,
            get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )

        st.session_state.docs_loaded = True

    st.success("PDFs indexed successfully!")

if st.session_state.docs_loaded:

    history = get_session_history(session_id)

    for msg in history.messages:
        role = "user" if msg.type == "human" else "assistant"
        with st.chat_message(role):
            st.markdown(msg.content)

    prompt = st.chat_input("Ask a question about your PDFs...")

    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("Thinking..."):
            response = st.session_state.rag_chain.invoke(
                {"input": prompt},
                config={
                    "configurable": {
                        "session_id": session_id
                    }
                }
            )

        with st.chat_message("assistant"):
            st.markdown(response["answer"])

            if "context" in response:
                with st.expander("Sources"):
                    for i, doc in enumerate(response["context"], 1):
                        page = doc.metadata.get("page", "Unknown")
                        st.markdown(f"**Chunk {i} (Page {page})**")
                        st.write(doc.page_content[:400] + "...")

elif not api_key:
    st.info("Enter your Groq API key to begin.")

elif not uploaded_files:
    st.info("Upload one or more PDFs.")
