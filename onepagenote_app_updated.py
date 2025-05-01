import openai
import docx
import PyPDF2
import streamlit as st
import os
from docx import Document
import re

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    with open(pdf_file, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in range(len(reader.pages)):
            text += reader.pages[page].extract_text()
    return text

# Function to extract text from DOCX
def extract_text_from_docx(docx_file):
    doc = Document(docx_file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

# Function to extract text from TXT
def extract_text_from_txt(txt_file):
    with open(txt_file, "r") as file:
        text = file.read()
    return text

# Function to extract and process commercials (price, payment terms, etc.)
def extract_commercials(text):
    commercials = []
    
    # Look for commercial details like price points, payment terms, etc.
    price_pattern = re.compile(r"\b(?:price|cost|fees?|amount|charges?)\b.*\d[\d,\.]*", re.IGNORECASE)
    payments_pattern = re.compile(r"\b(?:payment|installments?|due)\b.*\d[\d,\.]*", re.IGNORECASE)
    
    # Find matches
    price_matches = re.findall(price_pattern, text)
    payments_matches = re.findall(payments_pattern, text)
    
    if price_matches:
        commercials.append("Price Points / Amounts: \n" + "\n".join(price_matches))
    if payments_matches:
        commercials.append("Payment Terms: \n" + "\n".join(payments_matches))
    
    return "\n".join(commercials)

# Streamlit UI
st.title("Contract Summary Generator")

uploaded_file = st.file_uploader("Upload Contract (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])

if uploaded_file is not None:
    # Extract text based on file type
    file_type = uploaded_file.name.split('.')[-1].lower()
    if file_type == "pdf":
        text = extract_text_from_pdf(uploaded_file)
    elif file_type == "docx":
        text = extract_text_from_docx(uploaded_file)
    elif file_type == "txt":
        text = extract_text_from_txt(uploaded_file)
    
    # Call OpenAI API to generate contract summary
    openai.api_key = st.secrets["OPENAI_API_KEY"]
    
    # Prepare prompt for OpenAI
    prompt = f"""
    Summarize this contract in one page with the following sections:
    - Key Legal Points
    - Commercials (Price, Payment Terms, etc.)
    - Annexures (if any)
    
    Here's the contract text:
    {text}
    """
    
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",  # Using GPT model
            prompt=prompt,
            max_tokens=1500,
            temperature=0.7
        )

        summary = response.choices[0].text.strip()

        # Extract and show the commercial details
        commercials = extract_commercials(text)

        st.subheader("Contract Summary:")
        st.write(summary)

        if commercials:
            st.subheader("Commercials:")
            st.write(commercials)

    except openai.error.OpenAIError as e:
        st.error(f"Error: {e}")
