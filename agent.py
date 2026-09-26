import os
import streamlit as st
from langchain_community.utilities import SQLDatabase
from langchain_groq import ChatGroq
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import create_sql_agent

# 1. Securely load credentials from Streamlit Cloud Secrets
# (This acts as a bridge so LangChain can find the Groq API key automatically)
os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
NEON_DB_URL = st.secrets["NEON_DB_URL"]

def run_agent(user_prompt):
    # 2. Initialize Database Connection
    db = SQLDatabase.from_uri(NEON_DB_URL)
    
    # 3. Initialize the LLM (Update the model name if you used a different one)
    llm = ChatGroq(
        model_name="llama3-70b-8192", 
        temperature=0
    )
    
    # 4. Bind the Toolkit (This must happen AFTER db and llm are defined)
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    
    # 5. Create and Execute the Agent
    agent_executor = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True,
        handle_parsing_errors=True
    )
    
    # 6. Run the query and return the response
    response = agent_executor.invoke({"input": user_prompt})
    return response["output"]