import os
import streamlit as st
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_groq import ChatGroq
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.agent_toolkits import create_sql_agent

load_dotenv()

# 1. Fetch credentials (works locally via .env OR in the cloud via st.secrets)
neon_url_raw = os.getenv("NEON_DB_URL") or st.secrets["NEON_DB_URL"]
groq_key = os.getenv("GROQ_API_KEY") or st.secrets["GROQ_API_KEY"]

neon_url = neon_url_raw.replace("postgres://", "postgresql://")

# 2. Initialize Database and LLM without the try/except blocks
db = SQLDatabase.from_uri(neon_url)

llm = ChatGroq(
    groq_api_key=groq_key,
    model_name="openai/gpt-oss-120b",
    temperature=0
)

# 3. Create the Database Toolkit
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

# 4. Set Guardrails
custom_instructions = """You are an expert Real Estate Data Analyst AI for the National Capital Region (NCR) of India.
Your strictly defined job is to answer user questions by writing and executing PostgreSQL queries against the 'rental_listings' table.

GUARDRAIL: 
- You must ONLY answer questions using data retrieved from the 'rental_listings' table. 
- Refuse general questions, coding questions, or non-real estate questions politely.

SCHEMA RULES:
- `bhk` represents bedrooms.
- Always use ILIKE for text matching to avoid case sensitivity (e.g., city ILIKE 'noida').
- ALWAYS use LIMIT 10 on large results unless asked otherwise.
- Only execute SELECT queries. NEVER DML operations.
"""

# 5. Initialize the SQL Agent
agent_executor = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    prefix=custom_instructions,
    agent_type="tool-calling"
)

# --- STREAMLIT BRIDGE FUNCTION ---
def run_agent(user_query):
    """Bridge function to allow Streamlit to query the LangChain agent."""
    response = agent_executor.invoke({"input": user_query})
    return response["output"]