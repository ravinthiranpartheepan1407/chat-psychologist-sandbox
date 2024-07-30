# import pandas as pd
# import requests
# import os
#
# def download_pdf_from_url(url, filename):
#     try:
#         response = requests.get(url)
#         if response.status_code == 200:
#             with open(filename, 'wb') as f:
#                 f.write(response.content)
#             print(f"Downloaded: {filename}")
#         else:
#             print(f"Failed to download: {filename}, Status code: {response.status_code}")
#     except Exception as e:
#         print(f"Error downloading {filename}: {str(e)}")
#
# # Path to your CSV file
# csv_file = './Data.csv'
#
# # Directory to save downloaded PDFs
# output_dir = 'downloaded_pdfs'
# if not os.path.exists(output_dir):
#     os.makedirs(output_dir)
#
# # Read CSV into DataFrame
# try:
#     df = pd.read_csv(csv_file)
#     print(f"Loaded CSV with {len(df)} rows.")
# except Exception as e:
#     print(f"Error loading CSV: {str(e)}")
#     exit()
#
# # Iterate through each row and download PDFs
# for index, row in df.iterrows():
#     link = row['Link about Therapy']
#     language = row['Language']
#     filename = row['The name of the file']
#
#     if pd.isna(link):  # Skip rows with empty links
#         continue
#
#     # Ensure filename is valid
#     if pd.isna(filename) or not isinstance(filename, str):
#         filename = f"{language}_document_{index}.pdf"
#     else:
#         filename = filename.strip() + ".pdf"
#
#     # Download PDF from URL
#     download_path = os.path.join(output_dir, filename)
#     download_pdf_from_url(link, download_path)
#
# print("Download process completed.")
#
#
# import os
# import tempfile
# import requests
# import pandas as pd
# import streamlit as st
# from streamlit_chat import message
# from rag import ChatPDF
#
# st.set_page_config(
#     page_title="Chat Psychologist AI Sandbox"
# )
#
# st.markdown(
#     """
#     <style>
#     [data-testid="stAppViewContainer"] > .main {
#         background-color: 'black';
#         color: 'white';
#     }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )
#
# def display_messages():
#     st.subheader("RAG-NET Sandbox")
#     for i, (msg, is_user) in enumerate(st.session_state["messages"]):
#         message(msg, is_user=is_user, key=str(i))
#     st.session_state["thinking_spinner"] = st.empty()
#
# def process_input():
#     if st.session_state["user_input"] and len(st.session_state["user_input"].strip()) > 0:
#         user_text = st.session_state["user_input"].strip()
#         with st.session_state["thinking_spinner"], st.spinner("RAG-NET in Progress"):
#             agent_text = st.session_state["assistant"].ask(user_text)
#
#         st.session_state["messages"].append((user_text, True))
#         st.session_state["messages"].append((agent_text, False))
#
# def ingest_pdf(file_path):
#     with st.session_state["ingestion_spinner"], st.spinner(f"Ingesting {os.path.basename(file_path)}"):
#         st.session_state["assistant"].ingest(file_path)
#
# def load_pdfs_from_csv(csv_path):
#     st.session_state["assistant"].clear()
#     st.session_state["messages"] = []
#     st.session_state["user_input"] = ""
#
#     # Ingest DSM.pdf
#     dsm_path = "./DSM.pdf"
#     if os.path.exists(dsm_path):
#         ingest_pdf(dsm_path)
#     else:
#         st.error("DSM.pdf not found.")
#
#     # Read CSV and get the first 500 PDF links
#     df = pd.read_csv("./Data.csv")
#     pdf_links = df['Link about Therapy'].head(500)
#
#     for pdf_url in pdf_links:
#         response = requests.get(pdf_url)
#         if response.status_code == 200:
#             with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tf:
#                 tf.write(response.content)
#                 file_path = tf.name
#             ingest_pdf(file_path)
#             os.remove(file_path)
#         else:
#             st.error(f"Failed to download PDF from {pdf_url}")
#
# def page():
#     if len(st.session_state) == 0:
#         st.session_state["messages"] = []
#         st.session_state["assistant"] = ChatPDF()
#
#     st.header("Chat Psychologist AI Sandbox")
#
#     st.subheader("Upload a document")
#     csv_path = st.text_input("Enter path to CSV file with PDF links:")
#     if st.button("Load PDFs from CSV"):
#         load_pdfs_from_csv(csv_path)
#
#     st.session_state["ingestion_spinner"] = st.empty()
#
#     display_messages()
#     st.text_input("Message", key="user_input", on_change=process_input)
#
# if __name__ == "__main__":
#     page()