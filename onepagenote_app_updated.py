import streamlit as st
import tempfile
import os
from docx import Document
import PyPDF2
import openai

# Load Together API key from Streamlit secrets
api_key = st.secrets["TOGETHER_API_KEY"]
client = openai.OpenAI(api_key=api_key, base_url="https://api.together.xyz/v1")

# Function to extract text from uploaded files
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
        You are a legal expert. Your task is to summarize the contract in one page and provide details under the following key points:

        🔑 **Key Points in Legal Contracts**:
        
        1. **Parties Involved**:
            - Provide the full names and addresses of all parties.
            - Specify the legal capacity and authority of each party to sign the contract.

        2. **Purpose of the Contract**:
            - What is the clear statement of intent or scope of the contract?
            - Describe the goods, services, or responsibilities the contract addresses.

        3. **Terms and Conditions**:
            - What are the start and end dates of the contract (or is it ongoing)?
            - What are the payment terms (amount, mode, frequency)?
            - What are the obligations and duties of each party under the contract?

        4. **Deliverables and Timelines**:
            - What are the milestones or deadlines mentioned in the contract?
            - Are there any quality or performance expectations set in the contract?

        5. **Termination Clause**:
            - Under what conditions can the contract be terminated early?
            - What is the notice period for termination?

        6. **Confidentiality Clause**:
            - Are there any terms for non-disclosure of proprietary or sensitive information?

        7. **Dispute Resolution**:
            - What are the terms for mediation, arbitration, or jurisdiction for legal proceedings?

        8. **Liabilities and Indemnities**:
            - What risks are each party responsible for?
            - What compensation is due for losses, damages, or third-party claims?

        9. **Force Majeure**:
            - Does the contract contain any clauses protecting against unforeseeable events (e.g., natural disasters, war)?

        10. **Amendments and Modifications**:
            - How will changes to the agreement be made and documented?

        11. **Warranties and Representations**:
            - Are there any guarantees made by either party regarding facts or performance?

        12. **Governing Law**:
            - What laws (e.g., country or state) govern the contract?

        13. **Signatures and Dates**:
            - Who are the authorized representatives that signed the contract?
            - Are the dates and witnesses properly included?

        14. **Annexures or Schedules** (if any):
            - Are there supporting documents or detailed breakdowns attached at the end of the contract?

        Below is the contract text:
        {contract_text}
        """

        st.write("Generating summary...")

        try:
            response = client.chat.completions.create(
                model="mistralai/Mixtral-8x7B-Instruct-v0.1",
                messages=[
                    {"role": "system", "content": "You are a legal assistant. Summarize contracts with detailed breakdowns."},
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
