import streamlit as st
import tempfile
from PyPDF2 import PdfReader
import docx
import together

st.set_page_config(page_title="OnePageNote", layout="wide")

st.title("📄 OnePageNote - AI Contract Summarizer")

uploaded_file = st.file_uploader("Upload your contract (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])

def extract_text(file):
    if file.name.endswith(".pdf"):
        reader = PdfReader(file)
        return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    elif file.name.endswith(".docx"):
        doc = docx.Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    elif file.name.endswith(".txt"):
        return file.read().decode("utf-8")
    else:
        return ""

if uploaded_file:
    text = extract_text(uploaded_file)

    st.subheader("📜 Extracted Summary")
    with st.spinner("Analyzing contract..."):
        together.api_key = st.secrets["TOGETHER_API_KEY"]
        prompt = f"""
You are a legal assistant. Read the following contract and provide a one-page summary including the following sections:

1. **Parties Involved** – Full names, addresses, and capacity to sign.
2. **Purpose of the Contract** – Clear statement of intent.
3. **Terms and Conditions** – Duration, payment, and responsibilities.
4. **Deliverables and Timelines** – Milestones or quality expectations.
5. **Termination Clause** – Conditions and notice period.
6. **Confidentiality Clause** – Any restrictions on disclosure.
7. **Dispute Resolution** – Jurisdiction, arbitration, or mediation.
8. **Liabilities and Indemnities** – Risk and compensation.
9. **Force Majeure** – Events covered and their effects.
10. **Amendments and Modifications** – How changes are documented.
11. **Warranties and Representations** – Guarantees made by parties.
12. **Governing Law** – Which law governs this agreement.
13. **Signatures and Dates** – Signed by whom and when.
14. **Annexures or Schedules** – List and summarize annexures verbatim.

Contract Text:
{text}
"""

        response = together.chat.completions.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2048
        )

        summary = response.choices[0].message.content
        st.markdown(summary)
