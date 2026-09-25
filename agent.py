import os
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_groq import ChatGroq
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.agent_toolkits import create_sql_agent

load_dotenv()

print("\n=== STEP 1: Testing Connections ===")

# 1. Connect to Neon Database
try:
    neon_url = os.getenv("NEON_DB_URL").replace("postgres://", "postgresql://")
    db = SQLDatabase.from_uri(neon_url)
    print("✓ Database Connected! Usable Tables:", db.get_usable_table_names())
except Exception as e:
    print("❌ Database Connection Failed:", e)

# 2. Initialize Groq LLM
try:
    llm = ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name="openai/gpt-oss-120b",
        temperature=0
    )
    print("✓ Groq LLM Initialized!")
except Exception as e:
    print("❌ Groq LLM Failed:", e)

print("\n=== STEP 2: Building the Agent ===")

# 3. Create the Database Toolkit
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

# 4. Set our strict Real Estate Guardrails
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

# 5. Initialize the standard, stable SQL Agent
try:
    agent_executor = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True,
        prefix=custom_instructions,
        agent_type="tool-calling"
    )
    print("✓ SQL Agent Built Successfully!")
except Exception as e:
    print("❌ Agent Build Failed:", e)


print("\n=== STEP 3: Chat Loop ===")
if __name__ == "__main__":
    print("Type 'exit' or 'q' to stop.\n")
    while True:
        user_query = input("Ask a question about NCR rentals: ").strip()
        
        if user_query.lower() in ["exit", "quit", "q"]:
            print("Session ended.")
            break
        if not user_query:
            continue
            
        print("\n--- Agent Running ---")
        try:
            response = agent_executor.invoke({"input": user_query})
            print("\nFINAL ANSWER:\n", response["output"])
        except Exception as e:
            print("\nError executing query:", e)
        print("-" * 50)