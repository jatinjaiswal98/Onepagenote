import streamlit as st
import os
import fitz  # PyMuPDF
import tempfile
from together import Together

st.set_page_config(page_title="OnePageNote - Contract Summarizer", layout="wide")
st.title("📄 OnePageNote: Contract Summarizer")

uploaded_file = st.file_uploader("Upload a contract (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])

# Get Together API Key
api_key = st.secrets["TOGETHER_API_KEY"]
client = Together(api_key=api_key)

# Function to extract text from PDF
def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Function to split contract into main and annexure/signature parts
def split_contract_text(full_text):
    lines = full_text.strip().split("\n")
    total_lines = len(lines)
    cutoff = int(total_lines * 0.85)  # Last 15% as annexure
    main_body = "\n".join(lines[:cutoff])
    annexure_section = "\n".join(lines[cutoff:])
    return main_body, annexure_section

# Prompt templates
main_prompt_template = '''You are a legal assistant. Extract and summarize the key points of this contract in one page. Include the following sections:

🔑 Key Points in Legal Contracts:
1. Parties Involved (names, addresses)
2. Purpose of the Contract (scope, services, goods)
3. Terms and Conditions (duration, payment, obligations)
4. Deliverables and Timelines
5. Termination Clause
6. Confidentiality Clause
7. Dispute Resolution
8. Liabilities and Indemnities
9. Force Majeure
10. Amendments and Modifications
11. Warranties and Representations
12. Governing Law

Text:
"""
{main_text}
"""
'''

annexure_prompt_template = '''You are a legal assistant. Extract:
1. Any complete annexures from this section.
2. Signature names and dates.

Text:
"""
{annexure_text}
"""
'''

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=uploaded_file.name) as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    with st.spinner("Extracting and analyzing contract text..."):
        # Extract full text
        full_text = extract_text_from_pdf(tmp_path)
        main_text, annexure_text = split_contract_text(full_text)

        # Get main summary
        main_prompt = main_prompt_template.format(main_text=main_text)
        main_response = client.chat.completions.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            messages=[
                {"role": "user", "content": main_prompt}
            ],
            max_tokens=2048,
            temperature=0.4,
        )
        main_summary = main_response.choices[0].message.content.strip()

        # Get annexure & signatures
        annexure_prompt = annexure_prompt_template.format(annexure_text=annexure_text)
        annexure_response = client.chat.completions.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            messages=[
                {"role": "user", "content": annexure_prompt}
            ],
            max_tokens=2048,
            temperature=0.4,
        )
        annexure_summary = annexure_response.choices[0].message.content.strip()

    st.subheader("📘 Contract Summary")
    st.markdown(main_summary)

    st.subheader("📎 Annexures & Signatures")
    st.markdown(annexure_summary)

    os.remove(tmp_path)
