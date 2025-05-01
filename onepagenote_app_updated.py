import streamlit as st
import fitz  # PyMuPDF
import docx
import os
import tempfile
from together import Together
import re

st.set_page_config(page_title="OnePageNote", layout="wide")
st.title("📄 OnePageNote - Contract Summary Tool")

uploaded_file = st.file_uploader("Upload a contract file (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])

def extract_text(file):
    ext = os.path.splitext(file.name)[-1]
    if ext == ".pdf":
        with fitz.open(stream=file.read(), filetype="pdf") as doc:
            texts = [page.get_text() for page in doc]
            annexures = "\n".join(texts[-3:])  # Last 3 pages
            full_text = "\n".join(texts)
    elif ext == ".docx":
        document = docx.Document(file)
        full_text = "\n".join([p.text for p in document.paragraphs])
        annexures = "\n".join([p.text for p in document.paragraphs[-30:]])  # Last 30 paragraphs
    else:
        full_text = file.read().decode("utf-8")
        annexures = "\n".join(full_text.splitlines()[-100:])  # Last 100 lines
    return full_text, annexures

def extract_signatures(text):
    matches = re.findall(r"(Signed by.*?on\s+.*?\d{4})", text, flags=re.IGNORECASE | re.DOTALL)
    if not matches:
        matches = re.findall(r"(Name.*?:.*?\n.*?Date.*?:.*?\d{4})", text, flags=re.IGNORECASE)
    return "\n\n".join(matches) if matches else "No clear signatures found."

def generate_summary(text, annexures, signatures):
    client = Together(api_key=st.secrets["TOGETHER_API_KEY"])
    prompt = f"""
You are a legal assistant. Extract and summarize the following contract.
The summary MUST include these sections:

🔑 Key Points in Legal Contracts
- Parties Involved (names, addresses)
- Purpose of the Contract
- Terms and Conditions (duration, payment, obligations)
- Deliverables and Timelines
- Termination Clause
- Confidentiality Clause
- Dispute Resolution
- Liabilities and Indemnities
- Force Majeure
- Amendments and Modifications
- Warranties and Representations
- Governing Law
- Signatures and Dates
- Annexures (summarized or listed separately)

Extract the summary from the below contract text:

--- CONTRACT START ---

{text}

--- ANNEXURES ---

{annexures}

--- SIGNATURES ---

{signatures}
"""
    response = client.chat.completions.create(
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2048
    )
    return response.choices[0].message.content.strip()

if uploaded_file:
    with st.spinner("Reading and analyzing the contract..."):
        full_text, annexures = extract_text(uploaded_file)
        signatures = extract_signatures(full_text)
        summary = generate_summary(full_text, annexures, signatures)
    st.subheader("🧾 One Page Summary")
    st.text_area("Result", value=summary, height=600)
