import sys
import os
import requests
import streamlit as st
from streamlit_chat import message
from rag import ChatPDF

# Set page configuration
st.set_page_config(
    page_title="Chat Psychologist AI Sandbox"
)

# Custom styling
st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] > .main {
        background-color: 'black';
        color: 'white';
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Function to display chat messages
def display_messages():
    st.subheader("RAG-NET Sandbox")
    for i, (msg, is_user) in enumerate(st.session_state["messages"]):
        message(msg, is_user=is_user, key=str(i))
    st.session_state["thinking_spinner"] = st.empty()

# Function to process user input
def process_input():
    if st.session_state["user_input"] and len(st.session_state["user_input"].strip()) > 0:
        user_text = st.session_state["user_input"].strip()
        with st.session_state["thinking_spinner"], st.spinner("RAG-NET in Progress"):
            response = requests.get(f"https://arkhammapi.com/ask/?query={user_text}")
            agent_text = response.json().get("response", "Error: No response from the server.")

        st.session_state["messages"].append((user_text, True))
        st.session_state["messages"].append((agent_text, False))

# Function to upload and ingest a PDF file
def upload_and_ingest(file):
    st.session_state["assistant"].clear()
    st.session_state["messages"] = []
    st.session_state["user_input"] = ""

    # Upload the file to the API
    with st.session_state["ingestion_spinner"], st.spinner(f"Ingesting {file.name}"):
        form_data = {"file": file}
        response = requests.post('https://arkhammapi.com/upload/', files=form_data)
        if response.status_code == 200:
            st.success("File uploaded successfully and ingested.")
        else:
            st.error(f"Failed to upload file: {response.json().get('detail', 'Unknown error')}")

# Main page function
def page():
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
        st.session_state["assistant"] = ChatPDF()

    st.header("Chat Psychologist AI Sandbox")

    # File uploader for uploading PDF files
    st.subheader("Upload a document")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    if uploaded_file is not None:
        upload_and_ingest(uploaded_file)

    st.session_state["ingestion_spinner"] = st.empty()

    display_messages()
    st.text_input("Message", key="user_input", on_change=process_input)

# Run the main page function
if __name__ == "__main__":
    page()
