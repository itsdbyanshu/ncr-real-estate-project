import streamlit as st
from agent import run_agent

# 1. Page Configuration (Now with an expanded sidebar)
st.set_page_config(
    page_title="NCR Real Estate Analytics",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SIDEBAR: PORTFOLIO CONTEXT ---
with st.sidebar:
    st.title("🏙️ NCR Real Estate")
    st.markdown("An end-to-end data pipeline & AI project.")
    
    st.divider()
    
    st.markdown("### 👨‍💻 Built By")
    st.markdown("**Divyanshu Bhatt**")
    # Remember to replace these links with your actual URLs!
    st.markdown("[GitHub Profile](https://github.com/) | [LinkedIn](https://linkedin.com/)")
    
    st.divider()
    
    st.info(
        "**Architecture Note:**\n\n"
        "This UI integrates a static Power BI snapshot to bypass Microsoft's paid embed restrictions. "
        "However, the GenAI Data Assistant is **100% live**, querying an automated Neon PostgreSQL database in real-time."
    )

# --- MAIN PAGE HEADER ---
st.title("🏙️ Find the Property According to Your Needs")
st.markdown("Explore automated rental trends across Noida, Gurgaon, New Delhi, Ghaziabad, and Faridabad.")
st.divider()

# 2. Split into two columns with a larger gap for breathability
col1, col2 = st.columns([2, 1], gap="large")

# --- COLUMN 1: STATIC POWER BI DASHBOARD ---
with col1:
    st.subheader("📊 Live Market Dashboard")
    try:
        # Added a slight visual elevation using a markdown trick
        st.markdown("<br>", unsafe_allow_html=True)
        st.image("dashboard.png", use_container_width=True)
    except FileNotFoundError:
        st.warning("⚠️ Please place your dashboard image in the project folder and name it 'dashboard.png'.")

# --- COLUMN 2: GENAI SQL AGENT ---
with col2:
    st.subheader("🤖 Talk to the Database")
    
    with st.expander("💡 Pro-Tips for Asking Questions", expanded=False):
        st.markdown("""
        * **No Memory:** I treat every search independently.
        * **10-Result Limit:** Results are capped at 10. Ask to *"Show up to 50 results"* if needed.
        * **Be Exact:** Use objective metrics (*"rent under 20000"*, *"2 bhk"*).
        * **Spelling Matters:** Ensure city names are spelled correctly.
        
        **Try asking:**
        * *"What is the average rent for a 3 BHK in Faridabad?"*
        * *"Show the top 5 most expensive rentals in Gurgaon"*
        """)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Chat interface with slightly adjusted height to match the image better
    chat_container = st.container(height=500)
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    if prompt := st.chat_input("E.g., Find 2 BHK flats in Noida under ₹25,000..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Querying Neon database..."):
                    try:
                        response = run_agent(prompt)
                    except Exception as err:
                        response = f"**I couldn't process that request.** Please check your spelling. *(Error: {err})*"
                    st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})