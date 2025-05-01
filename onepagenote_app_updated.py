import streamlit as st
import PyPDF2
from transformers import pipeline

# Function to extract text from a PDF
def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    return text

# Initialize the Hugging Face summarization pipeline with Mistral-7B model
summarizer = pipeline("summarization", model="mistralai/Mistral-7B")

# Function to summarize the extracted text
def summarize_text(text):
    summary = summarizer(text, max_length=500, min_length=100, do_sample=False)
    return summary[0]['summary_text']

# Streamlit App UI
st.title("Contract Summary Tool")

# File uploader for PDF, DOCX, or TXT files
uploaded_file = st.file_uploader("Upload your contract (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])

if uploaded_file is not None:
    # Extract text based on file type
    if uploaded_file.type == "application/pdf":
        contract_text = extract_text_from_pdf(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        from docx import Document
        doc = Document(uploaded_file)
        contract_text = "\n".join([para.text for para in doc.paragraphs])
    elif uploaded_file.type == "text/plain":
        contract_text = str(uploaded_file.read(), "utf-8")

    # Display raw text
    st.subheader("Raw Contract Text")
    st.text_area("Contract Text", contract_text, height=300)

    # Generate the summary
    st.subheader("Generated Contract Summary")

    summary = summarize_text(contract_text)
    st.write(summary)

    # Enhanced format summary based on user request
    st.subheader("Formatted Contract Summary")

    # Placeholder summary format (Adjust accordingly based on specific requirements)
    formatted_summary = f"""
    1. **Parties Involved:**
    [Summary of parties involved]

    2. **Purpose:**
    [Summary of the purpose of the contract]

    3. **Terms:**
    [Summary of the terms]

    4. **Deliverables:**
    [Summary of the deliverables]

    5. **Termination:**
    [Summary of the termination clauses]

    6. **Confidentiality:**
    [Summary of the confidentiality clauses]

    7. **Dispute Resolution:**
    [Summary of the dispute resolution clauses]

    8. **Liabilities:**
    [Summary of liabilities]

    9. **Force Majeure:**
    [Summary of force majeure clauses]

    10. **Amendments:**
    [Summary of amendments clauses]

    11. **Warranties:**
    [Summary of warranties]

    12. **Governing Law:**
    [Summary of governing law]

    13. **Annexure Complete:**
    [Annexure content or summary]

    14. **Signatures:**
    [Summary of signatures]
    """
    st.text_area("Formatted Summary", formatted_summary, height=400)
