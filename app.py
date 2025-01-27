import streamlit as st

# ✅ Must be the first Streamlit command
st.set_page_config(page_title="Aviagen Chatbot", page_icon="🤖", layout="wide")

import os
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent

# Set OpenAI API Key
os.environ["OPENAI_API_KEY"] = "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"  # Replace with your actual API key

# ✅ Cache database connection
@st.cache_resource
def get_database():
    return SQLDatabase.from_uri("sqlite:///C:/Users/Acer/Documents/is571/CandlingData.db")

# ✅ Cache agent creation
@st.cache_resource
def get_agent():
    db = get_database()
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    return create_sql_agent(llm, db=db, agent_type="openai-tools", verbose=False)

# Initialize agent
agent_executor = get_agent()

# ✅ Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "followup_question" not in st.session_state:
    st.session_state.followup_question = None  # Stores clicked follow-up question

# ✅ Display chatbot title
st.markdown("<h1 style='text-align: center; color: #3498db;'>Aviagen Chatbot</h1>", unsafe_allow_html=True)

# ✅ Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ✅ User input box
user_input = st.chat_input("Ask me anything about the data...")

def clean_response(response):
    """Remove unwanted 'input' and 'output' words from the response."""
    if isinstance(response, dict):  # If response is a dictionary, extract only relevant content
        response = response.get("output", response.get("response", "No valid response."))
    return response

# ✅ Function to process queries (both user input and follow-ups)
def process_query(query):
    with st.spinner("Fetching data..."):
        response = agent_executor.invoke(query)
        response = clean_response(response)  # ✅ Clean up the response

    # ✅ Add question & response to chat history
    st.session_state.chat_history.append({"role": "user", "content": query})
    st.session_state.chat_history.append({"role": "assistant", "content": response})

    # ✅ Display response
    with st.chat_message("assistant"):
        st.markdown(response)

# ✅ Handle User Input
if user_input:
    process_query(user_input)

# ✅ Handle Follow-Up Question Click
if st.session_state.followup_question:
    process_query(st.session_state.followup_question)
    st.session_state.followup_question = None  # Reset follow-up state after processing

# ✅ Generate Follow-up Questions
followup_questions = []
if user_input:
    if "hatchability" in user_input.lower():
        followup_questions = [
            "Show hatchability breakdown by week",
            "Compare hatchability with other months",
            "How can I improve hatchability?"
        ]
    elif "rot" in user_input.lower():
        followup_questions = [
            "Show trends of rot quantity over time",
            "Compare with previous months",
            "What causes higher rot percentages?"
        ]
    elif "quantity" in user_input.lower():
        followup_questions = [
            "Show total production numbers",
            "Analyze trends in quantity candled",
            "Compare with last year's data"
        ]

# ✅ Display Follow-up Questions (Now Works Correctly!)
if followup_questions:
    st.markdown("### Follow-up Questions:")
    for q in followup_questions:
        if st.button(q, key=q):  # ✅ Store follow-up question in session state
            st.session_state.followup_question = q
            st.experimental_rerun()  # 🔄 Forces the UI to refresh and process the follow-up
