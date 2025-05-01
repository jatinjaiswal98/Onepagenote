import streamlit as st
from together import Together
import PyPDF2
import docx
from io import BytesIO

# Initialize Together client
client = Together(api_key=st.secrets["TOGETHER_API_KEY"])  # Replace with your actual Together API key

# Function to read PDF files
def read_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Function to read DOCX files
def read_docx(file):
    doc = docx.Document(file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

# Function to process and summarize contract text
def summarize_contract(text):
    response = client.chat.completions.create(
        model="mistralai/Mistral-7B-Instruct-v0.1",  # Adjust the model as needed
        messages=[
            {"role": "system", "content": "You are a legal assistant. Extract a detailed contract summary."},
            {"role": "user", "content": text}
        ]
    )
    summary = response["choices"][0]["message"]["content"]
    return summary

# Streamlit app layout
st.title("Contract Summary Tool")
st.write("Upload a contract in PDF, DOCX, or TXT format and receive a one-page summary.")

# File upload
uploaded_file = st.file_uploader("Choose a contract file", type=["pdf", "docx", "txt"])

if uploaded_file is not None:
    # Check the file type
    file_extension = uploaded_file.name.split('.')[-1].lower()

    # Read file content based on file type
    if file_extension == "pdf":
        contract_text = read_pdf(uploaded_file)
    elif file_extension == "docx":
        contract_text = read_docx(uploaded_file)
    elif file_extension == "txt":
        contract_text = uploaded_file.read().decode("utf-8")
    else:
        st.error("Unsupported file type.")
        contract_text = ""

    # Summarize the contract
    if contract_text:
        st.write("Generating summary...")
        summary = summarize_contract(contract_text)
        st.subheader("Contract Summary")
        st.write(summary)
