import streamlit as st
import requests
import json
import fitz  # PyMuPDF

st.set_page_config(page_title="OnePageNote", layout="wide")

st.title("📄 OnePageNote - Contract Summary Tool")

api_key = st.secrets["TOGETHER_API_KEY"]  # Set this in Streamlit Cloud Secrets

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

def extract_text_from_pdf(pdf_file):
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        full_text = ""
        for page in doc:
            full_text += page.get_text()
    return full_text

def extract_annexures(text):
    lines = text.split("\n")
    annexure_start = None
    for i, line in enumerate(lines[::-1]):  # Start from the end
        if "annexure" in line.lower() or "schedule" in line.lower():
            annexure_start = len(lines) - i - 1
            break
    if annexure_start is not None:
        return "\n".join(lines[annexure_start:])
    return ""

uploaded_file = st.file_uploader("Upload a contract document (PDF)", type=["pdf"])

if uploaded_file:
    with st.spinner("Extracting content..."):
        contract_text = extract_text_from_pdf(uploaded_file)
        annexure_text = extract_annexures(contract_text)
        combined_text = contract_text + "\n\n---\n\nANNEXURE SECTION:\n" + annexure_text

    prompt = f"""
You are a contract analysis assistant. Read the full text below and create a complete one-page summary including these sections:

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
14. **Annexures or Schedules (summarize key points if present)**
15. **Commercials** (highlight any price, cost, fees, penalties, payment schedules)

Focus on both **legal clauses** and **commercial elements** clearly.

Contract Content:
\"\"\"
{combined_text}
\"\"\"
"""

    with st.spinner("Generating contract summary..."):
        summary = query_together(prompt)

    st.subheader("📌 One-Page Contract Summary")
    st.markdown(summary)
