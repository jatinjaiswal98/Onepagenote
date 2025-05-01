import streamlit as st
import requests
import base64
import os
from docx import Document

st.title("📄 OnePageNote - Contract Summarizer")

uploaded_file = st.file_uploader("Upload a contract (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])

def extract_text(file):
    if file.name.endswith(".txt"):
        return file.read().decode("utf-8")
    elif file.name.endswith(".docx"):
        doc = Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    elif file.name.endswith(".pdf"):
        from PyPDF2 import PdfReader
        reader = PdfReader(file)
        return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    return ""

def query_together_ai(prompt, api_key):
    url = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "mistralai/Mistral-7B-Instruct-v0.1",
        "messages": [
            {"role": "system", "content": "You are a legal expert. Summarize this contract in one page. Include key terms, obligations, parties, duration, annexures, and notable clauses."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1024,
        "temperature": 0.5
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()["choices"][0]["message"]["content"]

if uploaded_file:
    text = extract_text(uploaded_file)
    if text:
        st.info("Extracting and summarizing contract...")
        api_key = st.secrets["TOGETHER_API_KEY"]  # Set in Streamlit Cloud secrets
        summary = query_together_ai(text, api_key)
        st.subheader("📌 One-Page Summary:")
        st.write(summary)
    else:
        st.error("Couldn't read the file.")
