import streamlit as st
import os
import tempfile
import fitz  # PyMuPDF
import docx
import openai
from PyPDF2 import PdfReader

# Set your Together API key here
api_key = st.secrets.get("TOGETHER_API_KEY")
client = openai.OpenAI(api_key=api_key, base_url="https://api.together.xyz")

st.set_page_config(page_title="OnePageNote - Contract Summary", layout="centered")
st.title("📄 OnePageNote - Contract Summary Tool")

uploaded_file = st.file_uploader("Upload Contract (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])

def extract_text(file):
    if file.name.endswith(".pdf"):
        text = ""
        pdf = PdfReader(file)
        for page in pdf.pages:
            text += page.extract_text() or ""
        return text
    elif file.name.endswith(".docx"):
        doc = docx.Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    elif file.name.endswith(".txt"):
        return file.read().decode("utf-8")
    return ""

def extract_annexures(text):
    lines = text.splitlines()
    annexure_section = ""
    capture = False
    for i in range(len(lines)-1, -1, -1):
        if any(word.lower() in lines[i].lower() for word in ["annexure", "appendix", "schedule"]):
            capture = True
        if capture:
            annexure_section = lines[i] + "\n" + annexure_section
    return annexure_section.strip()

def extract_signatures(text):
    lines = text.splitlines()
    signature_lines = []
    for line in lines[-100:]:
        if any(keyword in line.lower() for keyword in ["signed", "signature", "date", "by", "on behalf"]):
            signature_lines.append(line)
    return "\n".join(signature_lines).strip()

def format_prompt(text, annexures, signatures):
    prompt = f"""
You are a legal assistant. Extract the following key sections from the given contract and create a clear, structured one-page summary. Follow the exact format and fill in every section:

🔑 Key Points in Legal Contracts

**Parties Involved**
- Full names and addresses
- Legal authority

**Purpose of the Contract**
- Intent and scope
- Goods/services/responsibilities

**Terms and Conditions**
- Duration (start/end)
- Payment terms
- Obligations

**Deliverables and Timelines**
- Key milestones
- Deadlines
- Quality/performance expectations

**Termination Clause**
- Conditions to terminate
- Notice period

**Confidentiality Clause**
- Non-disclosure obligations

**Dispute Resolution**
- Legal process and jurisdiction

**Liabilities and Indemnities**
- Risk allocation
- Compensation

**Force Majeure**
- Unforeseeable event handling

**Amendments and Modifications**
- How changes are managed

**Warranties and Representations**
- Promises or guarantees made

**Governing Law**
- Applicable law

**Annexures**
{annexures or 'No annexures found'}

**Signatures and Dates**
{signatures or 'Signatures not clearly found'}

Here is the contract:
{text[:15000]}
"""
    return prompt

if uploaded_file:
    with st.spinner("Processing file and generating summary..."):
        raw_text = extract_text(uploaded_file)
        annexures = extract_annexures(raw_text)
        signatures = extract_signatures(raw_text)
        full_prompt = format_prompt(raw_text, annexures, signatures)

        try:
            response = client.chat.completions.create(
                model="mistralai/Mixtral-8x7B-Instruct-v0.1",
                messages=[{"role": "user", "content": full_prompt}],
                max_tokens=2048,
                temperature=0.3
            )
            summary = response.choices[0].message.content.strip()
            st.success("✅ Summary generated successfully!")
            st.text_area("📄 Contract Summary", summary, height=600)
        except Exception as e:
            st.error(f"Error generating summary: {str(e)}")
