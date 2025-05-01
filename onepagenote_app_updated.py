import openai
import streamlit as st
from PyPDF2 import PdfReader
from docx import Document

# Set up OpenAI API key and model
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Function to handle the contract summarization
def summarize_contract(contract_text):
    prompt = """
    Summarize this contract in a structured format with all the following sections:

    1. Parties Involved: (Full names and addresses of all parties, legal authority to sign)
    2. Purpose of the Contract: (Clear statement of intent or scope)
    3. Terms and Conditions: (Duration, payment terms, obligations)
    4. Deliverables and Timelines: (Milestones, deadlines, performance expectations)
    5. Termination Clause: (Conditions for early termination, notice period)
    6. Confidentiality Clause: (Non-disclosure terms)
    7. Dispute Resolution: (Mediation, arbitration details, jurisdiction)
    8. Liabilities and Indemnities: (Risk-bearing, compensation clauses)
    9. Force Majeure: (Protection against unforeseen events)
    10. Amendments and Modifications: (How contract changes are documented)
    11. Warranties and Representations: (Guarantees made by the parties)
    12. Governing Law: (Applicable jurisdiction or country's laws)
    13. Signatures and Dates: (Names, roles, and dates of signatures)
    14. Annexures: (Any supporting documents attached at the end)

    Ensure the summary is well-formatted and covers all points listed above. If any section is missing, indicate it as "Not specified in the contract."
    """
    
    try:
        # Call OpenAI API to get summary
        response = openai.Completion.create(
            engine="text-davinci-003",  # You can switch to the model you are using
            prompt=prompt + "\n\n" + contract_text,
            max_tokens=1500,
            temperature=0.7
        )
        return response.choices[0].text.strip()
    
    except Exception as e:
        return f"An error occurred: {e}"

# Function to extract text from PDF file
def read_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    contract_text = ""
    for page in reader.pages:
        contract_text += page.extract_text()
    return contract_text

# Function to extract text from DOCX file
def read_docx(docx_file):
    doc = Document(docx_file)
    contract_text = ""
    for para in doc.paragraphs:
        contract_text += para.text
    return contract_text

# Streamlit code for user interface
st.title("Contract Summarization Tool")

uploaded_file = st.file_uploader("Upload a contract file", type=["pdf", "docx", "txt"])

if uploaded_file:
    # Read the contract text
    if uploaded_file.type == "application/pdf":
        contract_text = read_pdf(uploaded_file)  # Extract text from PDF
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        contract_text = read_docx(uploaded_file)  # Extract text from DOCX file
    else:
        contract_text = uploaded_file.read().decode("utf-8")  # Read text from plain text file

    # Generate the summary
    summary = summarize_contract(contract_text)

    # Display the summary
    st.subheader("Contract Summary")
    st.text_area("Summary", summary, height=400)
