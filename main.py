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
            try:
                response = requests.get(f"https://arkhammapi.com/ask/?query={user_text}")
                response.raise_for_status()
                agent_text = response.json().get("response", "Error: No response from the server.")
            except requests.exceptions.RequestException as e:
                agent_text = f"Error: {e}"
            except ValueError as e:
                agent_text = f"Error: Unable to decode JSON response: {e}"

        st.session_state["messages"].append((user_text, True))
        st.session_state["messages"].append((agent_text, False))

# Function to load predefined PDFs
def load_predefined_pdfs():
    st.session_state["assistant"].clear()
    st.session_state["messages"] = []
    st.session_state["user_input"] = ""

    predefined_pdf_paths = [
        "./DSM.pdf",
    ]

    for file_path in predefined_pdf_paths:
        with st.session_state["ingestion_spinner"], st.spinner(f"Ingesting {os.path.basename(file_path)}"):
            try:
                with open(file_path, "rb") as file:
                    form_data = {"file": (os.path.basename(file_path), file, "application/pdf")}
                    response = requests.post('https://arkhammapi.com/upload/', files=form_data)
                    response.raise_for_status()
                    st.success(f"{os.path.basename(file_path)} uploaded successfully and ingested.")
            except requests.exceptions.RequestException as e:
                st.error(f"Failed to upload {os.path.basename(file_path)}: {e}")

# Main page function
def page():
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
        st.session_state["assistant"] = ChatPDF()

    st.header("Chat Psychologist AI Sandbox")

    st.subheader("Upload a document")
    if st.button("Load Predefined PDFs"):
        load_predefined_pdfs()

    st.session_state["ingestion_spinner"] = st.empty()

    display_messages()
    st.text_input("Message", key="user_input", on_change=process_input)

# Run the main page function
if __name__ == "__main__":
    page()
