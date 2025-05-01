import streamlit as st
import openai
from docx import Document
import PyPDF2
import re

# Set up OpenAI API
openai.api_key = st.secrets["OPENAI_API_KEY"]

def extract_text_from_pdf(pdf_file):
    """Extract text from a PDF file."""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_docx(docx_file):
    """Extract text from a DOCX file."""
    doc = Document(docx_file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def extract_text_from_txt(txt_file):
    """Extract text from a TXT file."""
    return txt_file.read().decode("utf-8")

def extract_commercial_terms(text):
    """Extract commercial terms and highlight prices mentioned."""
    commercial_terms = []

    # Regular expression to find prices (e.g., amounts like ₹1000, $500)
    price_pattern = r'(\₹|\$|€|£)?\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?'

    prices = re.findall(price_pattern, text)
    if prices:
        commercial_terms.append(f"Prices mentioned: {', '.join(prices)}")

    # Adding more commercial-related aspects like payment terms
    payment_terms = ["payment", "amount", "charges", "penalties", "fees"]
    for term in payment_terms:
        if term in text.lower():
            commercial_terms.append(f"Commercial term found: '{term}'")

    return commercial_terms, prices

def summarize_contract(text):
    """Use OpenAI to generate a summary of the contract with business/commercial focus."""
    prompt = f"Summarize this contract in one page, including legal aspects, business/commercial terms (such as pricing, payments, penalties, etc.), parties involved, deliverables, annexures, and any notable clauses:\n\n{text}"
    
    response = openai.Completion.create(
        model="text-davinci-003",  # or use any model that suits your needs
        prompt=prompt,
        temperature=0.5,
        max_tokens=1500,
        n=1,
        stop=None,
    )
    
    summary = response.choices[0].text.strip()
    return summary

def extract_annexures(text):
    """Extract annexures (if available in the contract) from the text."""
    annexure_section = []
    annexure_start = text.lower().find("annexure")
    if annexure_start != -1:
        annexure_section = text[annexure_start:]
    return annexure_section

# Streamlit app
st.title("Contract Summary Tool")

st.write("Upload a contract in PDF, DOCX, or TXT format to receive a one-page summary with both legal and business/commercial points.")

uploaded_file = st.file_uploader("Choose a contract file", type=["pdf", "docx", "txt"])

if uploaded_file is not None:
    file_extension = uploaded_file.name.split(".")[-1].lower()

    # Extract text from the uploaded file
    if file_extension == "pdf":
        text = extract_text_from_pdf(uploaded_file)
    elif file_extension == "docx":
        text = extract_text_from_docx(uploaded_file)
    elif file_extension == "txt":
        text = extract_text_from_txt(uploaded_file)
    else:
        st.error("Invalid file type. Please upload a PDF, DOCX, or TXT file.")
        text = ""

    if text:
        # Extract commercial terms and prices
        commercial_terms, prices = extract_commercial_terms(text)

        # Summarize the contract
        summary = summarize_contract(text)

        # Extract annexures
        annexures = extract_annexures(text)

        # Combine everything for display
        full_summary = f"### Contract Summary:\n\n{summary}"

        # Display commercial details
        if commercial_terms:
            full_summary += f"\n\n### Commercial Terms:\n{', '.join(commercial_terms)}"
        
        # Highlight prices
        if prices:
            full_summary += f"\n\n### Prices Mentioned:\n{', '.join(prices)}"

        # Add annexures (if available)
        if annexures:
            full_summary += f"\n\n### Annexures:\n{''.join(annexures)}"

        # Display the final summary
        st.write(full_summary)

        # Display file download option
        st.download_button(
            label="Download Contract Summary",
            data=full_summary,
            file_name="contract_summary.txt",
            mime="text/plain"
        )

