import os
import tempfile
import streamlit as st
from streamlit_chat import message
from rag import ChatPDF

st.set_page_config(
    page_title="Chat Psychologist AI Sandbox"
)

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

def display_messages():
    st.subheader("RAG-NET Sandbox")
    for i, (msg, is_user) in enumerate(st.session_state["messages"]):
        message(msg, is_user=is_user, key=str(i))
    st.session_state["thinking_spinner"] = st.empty()

def process_input():
    if st.session_state["user_input"] and len(st.session_state["user_input"].strip()) > 0:
        user_text = st.session_state["user_input"].strip()
        with st.session_state["thinking_spinner"], st.spinner("RAG-NET in Progress"):
            agent_text = st.session_state["assistant"].ask(user_text)

        st.session_state["messages"].append((user_text, True))
        st.session_state["messages"].append((agent_text, False))

def load_predefined_pdfs():
    st.session_state["assistant"].clear()
    st.session_state["messages"] = []
    st.session_state["user_input"] = ""

    predefined_pdf_paths = [
        "./DSM.pdf",
    ]

    for file_path in predefined_pdf_paths:
        with st.session_state["ingestion_spinner"], st.spinner(f"Ingesting {os.path.basename(file_path)}"):
            st.session_state["assistant"].ingest(file_path)

def page():
    if len(st.session_state) == 0:
        st.session_state["messages"] = []
        st.session_state["assistant"] = ChatPDF()

    st.header("Chat Psychologist AI Sandbox")

    st.subheader("Upload a document")
    if st.button("Load Predefined PDFs"):
        load_predefined_pdfs()

    st.session_state["ingestion_spinner"] = st.empty()

    display_messages()
    st.text_input("Message", key="user_input", on_change=process_input)

if __name__ == "__main__":
    page()


# from fastapi import FastAPI, File, UploadFile, HTTPException, Body, Form
# from fastapi.middleware.cors import CORSMiddleware
# import uvicorn
# from pytube import YouTube
# import moviepy.editor as mp
# import speech_recognition as sr
# from fpdf import FPDF
# import os
# from langchain_community.document_loaders import PyPDFLoader
# from langchain_community.vectorstores import Chroma
# from langchain_community.chat_models import ChatOllama
# from langchain_community.embeddings import FastEmbedEmbeddings
# from langchain.schema.output_parser import StrOutputParser
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.schema.runnable import RunnablePassthrough
# from langchain.prompts import PromptTemplate
# from langchain.vectorstores.utils import filter_complex_metadata
# from fastapi.responses import FileResponse, JSONResponse
# from googletrans import Translator
# from gtts import gTTS
# import pyttsx3
#
# from rag import ChatPDF  # Assuming your class is saved in this module
#
# app = FastAPI()
#
# # CORS for frontend interaction
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # You should specify the actual origins in production
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
# # Create an instance of ChatPDF
# chat_pdf = ChatPDF()
#
#
# @app.post("/upload/")
# async def upload_pdf(file: UploadFile = File(...)):
#     if not file.filename.endswith('.pdf'):
#         raise HTTPException(status_code=400, detail="Invalid file format. Please upload a PDF.")
#     try:
#         contents = await file.read()
#         with open(f"temp_{file.filename}", "wb") as f:
#             f.write(contents)
#         chat_pdf.ingest(f"temp_{file.filename}")
#         return {"message": "PDF uploaded and processed successfully"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
#
#
# @app.get("/ask/")
# async def ask_question(query: str):
#     response = chat_pdf.ask(query)
#     return {"response": response}
#
#
# @app.post("/clear/")
# def clear_data():
#     chat_pdf.clear()
#     return {"message": "Data cleared successfully"}
#
#
# class ChatVideo:
#     def __init__(self):
#         self.model = ChatOllama(model="mistral")
#         self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=100)
#         self.prompt = PromptTemplate.from_template("""Your template here""")
#         self.vector_store = None
#         self.retriever = None
#         self.chain = None
#
#     def ingest(self, pdf_file_path: str):
#         docs = PyPDFLoader(file_path=pdf_file_path).load()
#         chunks = self.text_splitter.split_documents(docs)
#         chunks = filter_complex_metadata(chunks)
#         self.vector_store = Chroma.from_documents(documents=chunks, embedding=FastEmbedEmbeddings())
#         self.retriever = self.vector_store.as_retriever(search_type="similarity_score_threshold", search_kwargs={"k": 3, "score_threshold": 0.5})
#         self.chain = ({"context": self.retriever, "question": RunnablePassthrough()} | self.prompt | self.model | StrOutputParser())
#
#     def ask(self, query: str):
#         if not self.chain:
#             return "Please, add a PDF document first."
#         return self.chain.invoke(query)
#
#     def clear(self):
#         self.vector_store = None
#         self.retriever = None
#         self.chain = None
#
#
# chat_video = ChatVideo()
#
#
# @app.post("/video_process_youtube/")
# def process_youtube_video(youtube_url: str = Body(..., embed=True)):
#     if not youtube_url.startswith("https://www.youtube.com"):
#         raise HTTPException(status_code=400, detail="Invalid YouTube URL.")
#
#     try:
#         yt = YouTube(youtube_url)
#         audio_stream = yt.streams.filter(only_audio=True).first()
#         if not audio_stream:
#             raise HTTPException(status_code=404, detail="No audio stream available for this video.")
#
#         audio_stream.download(filename='temp_audio.mp4')
#
#         clip = mp.AudioFileClip('temp_audio.mp4')
#         clip.write_audiofile('temp_audio.wav')
#         clip.close()
#         # os.remove('temp_audio.mp4')
#
#         r = sr.Recognizer()
#         with sr.AudioFile("temp_audio.wav") as source:
#             audio_data = r.record(source)
#             text = r.recognize_google(audio_data)
#             print(text)
#
#         pdf = FPDF()
#         pdf.add_page()
#         pdf.set_font("Arial", size=12)
#         pdf.multi_cell(0, 10, text)
#         pdf_file_path = "output_text.pdf"
#         gen = pdf.output(pdf_file_path)
#
#         os.remove('temp_audio.wav')
#
#         return FileResponse(path=pdf_file_path, media_type='application/pdf', filename='output_text.pdf')
#     except sr.UnknownValueError:
#         raise HTTPException(status_code=422, detail="Speech recognition could not understand audio.")
#     except sr.RequestError as e:
#         raise HTTPException(status_code=500, detail=f"Could not request results from Google Speech Recognition service; {e}")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
#
#
# @app.get("/video_ask_question/")
# async def ask_question(query: str):
#     response = chat_video.ask(query)
#     return {"response": response}
#
#
# @app.post("/translate/")
# async def translate_audio(file: UploadFile = File(...), language: str = Form(...)):
#     print("Received language code:", language)  # Debug: Check the received language code
#
#     # Save temporary audio file
#     temp_filename = f"temp_{file.filename}"
#     with open(temp_filename, 'wb') as buffer:
#         buffer.write(await file.read())
#
#     # Recognize speech
#     recognizer = sr.Recognizer()
#     with sr.AudioFile(temp_filename) as source:
#         audio_data = recognizer.record(source)
#     text = recognizer.recognize_google(audio_data)
#     print("Recognized text:", text)  # Debug: Check recognized text
#
#     # Translate text
#     translator = Translator()
#     try:
#         translated_text = translator.translate(text, dest='spanish').text
#     except Exception as e:
#         print("Translation error:", e)  # Debug: Check translation error
#         return JSONResponse(status_code=400, content={"error": str(e)})
#
#     # Text-to-Speech
#     engine = pyttsx3.init()
#     translated_filename = "translated_audio.mp3"
#     engine.save_to_file(translated_text, translated_filename)
#     engine.runAndWait()
#
#     # Cleanup and respond
#     os.remove(temp_filename)
#     return JSONResponse(content={"url": f"http://localhost:8000/{translated_filename}"})
#
#
# @app.post("/video_cleanup/")
# def cleanup():
#     try:
#         os.remove("output_text.pdf")
#         chat_video.clear()
#         return {"message": "Temporary files and cache cleared."}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
#
#
# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)
