import streamlit as st
import tempfile
import os
from docx import Document
import PyPDF2
import openai

# Load Together API key from Streamlit secrets
api_key = st.secrets["TOGETHER_API_KEY"]
client = openai.OpenAI(api_key=api_key, base_url="https://api.together.xyz/v1")

def extract_text(file):
    ext = file.name.split(".")[-1].lower()
    if ext == "txt":
        return file.read().decode("utf-8")
    elif ext == "pdf":
        reader = PyPDF2.PdfReader(file)
        text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
        return text
    elif ext == "docx":
        doc = Document(file)
        return "\n".join(paragraph.text for paragraph in doc.paragraphs)
    else:
        return "Unsupported file format"

st.title("📄 OnePageNote – Contract Summarizer")
uploaded_file = st.file_uploader("Upload a contract (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])

if uploaded_file:
    contract_text = extract_text(uploaded_file)
    if contract_text:
        st.success("File uploaded and read successfully!")

        prompt = f"""
        You are a legal analyst. Read the following contract and create a one-page summary. Include:
        - Names of all parties involved
        - Start and end dates / duration
        - Payment terms and obligations
        - Termination clauses
        - Governing law
        - Responsibilities of each party
        - Any penalties or breach clauses
        - Any referenced annexures and their summaries
        - Any unusual or important clauses

        Here is the contract:
        {contract_text}
        """

        st.write("Generating summary...")

        try:
            response = client.chat.completions.create(
                model="mistralai/Mixtral-8x7B-Instruct-v0.1",
                messages=[
                    {"role": "system", "content": "You are a legal assistant. Summarize contracts."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
            )
            summary = response.choices[0].message.content
            st.subheader("📋 One Page Summary:")
            st.write(summary)
        except Exception as e:
            st.error(f"Failed to generate summary: {e}")
    else:
        st.error("Could not read file content.")
