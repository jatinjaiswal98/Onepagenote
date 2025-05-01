import streamlit as st
import requests
import json
import fitz  # PyMuPDF
import docx2txt
import io

st.set_page_config(page_title="OnePageNote", layout="wide")

st.title("📄 OnePageNote - Contract Summary Tool")

api_key = st.secrets["TOGETHER_API_KEY"]  # Set in Streamlit Secrets

def query_together(prompt):
    url = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 4096,
        "temperature": 0.3
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        st.error("API Error: " + response.text)
        return "Error: Unable to fetch summary"

def extract_text(file):
    file_type = file.type
    if file_type == "application/pdf":
        with fitz.open(stream=file.read(), filetype="pdf") as doc:
            return "\n".join(page.get_text() for page in doc)
    elif file_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        return docx2txt.process(io.BytesIO(file.read()))
    elif file_type in ["text/plain"]:
        return file.read().decode("utf-8")
    else:
        st.error("Unsupported file type")
        return ""

def extract_annexures(text):
    lines = text.split("\n")
    annexure_start = None
    for i, line in enumerate(lines[::-1]):
        if "annexure" in line.lower() or "schedule" in line.lower():
            annexure_start = len(lines) - i - 1
            break
    if annexure_start is not None:
        return "\n".join(lines[annexure_start:])
    return ""

uploaded_file = st.file_uploader("Upload a contract (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])

if uploaded_file:
    with st.spinner("Extracting content..."):
        contract_text = extract_text(uploaded_file)
        annexure_text = extract_annexures(contract_text)
        full_content = contract_text + "\n\n---\n\nANNEXURE SECTION:\n" + annexure_text

    prompt = f"""
You are a contract analysis assistant. Read the full contract below and create a detailed one-page summary including:

1. **Parties Involved**
2. **Purpose of the Contract**
3. **Terms and Conditions** (start/end dates, payments, duties)
4. **Deliverables and Timelines**
5. **Termination Clause**
6. **Confidentiality Clause**
7. **Dispute Resolution**
8. **Liabilities and Indemnities**
9. **Force Majeure**
10. **Amendments and Modifications**
11. **Warranties and Representations**
12. **Governing Law**
13. **Signatures and Dates**
14. **Annexures or Schedules** (summarize AND include full annexure content)
15. **Commercials** (highlight any price, fees, penalties, payment schedules)

Use plain and clear formatting.

Contract:
\"\"\"
{full_content}
\"\"\"
"""

    with st.spinner("Generating contract summary..."):
        summary = query_together(prompt)

    st.subheader("📌 One-Page Contract Summary")
    st.markdown(summary)
