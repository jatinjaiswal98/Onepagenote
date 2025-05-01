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

        🔑 Key Points in Legal Contracts:
        - **Parties Involved**:
          - Full names and addresses of all parties
          - Legal capacity and authority to sign
        - **Purpose of the Contract**:
          - Clear statement of intent or scope
          - Description of services, goods, or responsibilities
        - **Terms and Conditions**:
          - Duration (start/end dates or ongoing)
          - Payment terms (amount, mode, frequency)
          - Obligations and duties of each party
        - **Deliverables and Timelines**:
          - Milestones or deadlines
          - Quality or performance expectations
        - **Termination Clause**:
          - Conditions under which the contract can be ended early
          - Notice period requirements
        - **Confidentiality Clause**:
          - Non-disclosure of proprietary or sensitive information
        - **Dispute Resolution**:
          - Mediation, arbitration, or jurisdiction for legal proceedings
        - **Liabilities and Indemnities**:
          - Who bears what risk
          - Compensation for losses, damages, or third-party claims
        - **Force Majeure**:
          - Protection against unforeseeable events (natural disasters, war, etc.)
        - **Amendments and Modifications**:
          - How changes to the agreement will be made and documented
        - **Warranties and Representations**:
          - Guarantees made by either party regarding facts or performance
        - **Governing Law**:
          - Which country/state's laws apply to the contract
        - **Signatures and Dates**:
          - Signed by authorized representatives
          - Properly dated and witnessed if required
        - **Annexures or Schedules** (if any):
          - Supporting documents or detailed breakdowns attached at the end

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
