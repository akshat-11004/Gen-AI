import streamlit as st
import os
import mysql.connector
from pathlib import Path
from langchain_classic.agents import create_sql_agent
from langchain_classic.sql_database import SQLDatabase
from langchain_classic.callbacks import StreamlitCallbackHandler
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy import create_engine
from sqlalchemy import exc as sqlalchemy_exc
from sqlalchemy.engine import URL
import sqlite3
from langchain_groq import ChatGroq

st.set_page_config(page_title="LangChain: Chat with SQL DB", page_icon="🦜")
st.title("🦜 LangChain: Chat with SQL DB")

LOCALDB="USE_LOCALDB"
MYSQL="USE_MYSQL"

radio_opt=["Use SQLLite 3 Database- Student.db","Connect to you MySQL Database"]

selected_opt=st.sidebar.radio(label="Choose the DB which you want to chat",options=radio_opt)

if radio_opt.index(selected_opt)==1:
    db_uri=MYSQL
    mysql_host=st.sidebar.text_input("Provide MySQL Host")
    mysql_user=st.sidebar.text_input("MYSQL User")
    mysql_password=st.sidebar.text_input("MYSQL password",type="password")
    mysql_db=st.sidebar.text_input("MySQL database")
    mysql_port=st.sidebar.number_input("MySQL port", min_value=1, max_value=65535, value=3306, step=1)
else:
    db_uri=LOCALDB

api_key=st.sidebar.text_input(label="Groq API Key",type="password").strip()

if not db_uri:
    st.info("Please enter the database information and uri")
    st.stop()

if not api_key:
    st.info("Please add the groq api key")
    st.stop()

# os.environ["GROQ_API_KEY"] = api_key

## LLM model
llm=ChatGroq(groq_api_key=api_key,model_name="openai/gpt-oss-120b",streaming=True,temperature=0.2)

def normalize_mysql_host(mysql_host, mysql_port):
    mysql_host = mysql_host.strip()
    if ":" in mysql_host and mysql_host.count(":") == 1:
        host, port = mysql_host.rsplit(":", 1)
        if port.isdigit():
            return host, int(port)
    return mysql_host, mysql_port

def show_database_error(error):
    original_error = getattr(error, "orig", error)
    error_number = getattr(original_error, "errno", None)

    st.error("Database connection failed.")

    if error_number == 2003:
        st.info("MySQL server is not reachable. Check that MySQL is running and the host/port are correct.")
    elif error_number == 2005:
        st.info("MySQL host is invalid. Use host `localhost` and port `3306` separately.")
    elif error_number == 1045:
        st.info("MySQL login failed. Check the username and password.")
    elif error_number == 1049:
        st.info("The selected MySQL database does not exist.")
    else:
        st.info("Check your MySQL host, port, username, password, database name, and server status.")

    st.caption(f"Driver error: {original_error}")
    st.stop()

def configure_db(db_uri,mysql_host=None,mysql_user=None,mysql_password=None,mysql_db=None,mysql_port=3306):
    if db_uri==LOCALDB:
        dbfilepath=(Path(__file__).parent/"student.db").absolute()
        print(dbfilepath)
        creator = lambda: sqlite3.connect(f"file:{dbfilepath}?mode=ro", uri=True)
        return SQLDatabase(create_engine("sqlite:///", creator=creator))
    elif db_uri==MYSQL:
        if not (mysql_host and mysql_user and mysql_password and mysql_db):
            st.error("Please provide all MySQL connection details.")
            st.stop()
        mysql_host, mysql_port = normalize_mysql_host(mysql_host, mysql_port)
        connection_url = URL.create(
            drivername="mysql+mysqlconnector",
            username=mysql_user,
            password=mysql_password,
            host=mysql_host,
            port=mysql_port,
            database=mysql_db,
        )
        engine = create_engine(connection_url)
        with engine.connect():
            pass
        return SQLDatabase(engine)
    
try:
    if db_uri==MYSQL:
        db=configure_db(db_uri,mysql_host,mysql_user,mysql_password,mysql_db,mysql_port)
    else:
        db=configure_db(db_uri)
except (mysql.connector.Error, sqlalchemy_exc.SQLAlchemyError) as error:
    show_database_error(error)

## toolkit
toolkit=SQLDatabaseToolkit(db=db,llm=llm)

agent=create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type="tool-calling"
)

if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_query=st.chat_input(placeholder="Ask anything from the database")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
        streamlit_callback=StreamlitCallbackHandler(st.container())
        try:
            response=agent.run(user_query,callbacks=[streamlit_callback])
            st.session_state.messages.append({"role":"assistant","content":response})
            st.write(response)
        except (mysql.connector.Error, sqlalchemy_exc.SQLAlchemyError) as error:
            show_database_error(error)
