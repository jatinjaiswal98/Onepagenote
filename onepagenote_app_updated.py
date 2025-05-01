import streamlit as st
import os
import tempfile
from PyPDF2 import PdfReader
import requests

# UI
st.set_page_config(page_title="OnePageNote: Contract Summary Tool", layout="wide")
st.title("📄 OnePageNote – AI Contract Summarizer")
st.markdown("Upload a contract file (PDF) to get a detailed one-page summary, including legal and commercial points, signatures, and annexures.")

# Upload
uploaded_file = st.file_uploader("Upload Contract (PDF)", type=["pdf"])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    # Read full contract
    reader = PdfReader(tmp_path)
    full_text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])

    # Extract last few pages as annexures
    last_pages_text = "\n".join([reader.pages[i].extract_text() or "" for i in range(max(0, len(reader.pages) - 5), len(reader.pages))])

    # Build prompt
    full_prompt = f"""
Summarize the following contract into a one-page detailed summary. The summary must include **both legal and commercial aspects**, focusing on:

1. **Parties Involved** – Names, roles, and authority.
2. **Purpose of the Contract** – Scope and intent.
3. **Terms and Conditions** – Duration, duties, obligations.
4. **Deliverables and Timelines** – Key milestones and expectations.
5. **Commercial Terms** – Pricing, payment schedule, taxes, penalties, invoice terms, logistics/delivery cost.
6. **Confidentiality Clause** – Obligations of secrecy.
7. **Dispute Resolution** – Arbitration/jurisdiction terms.
8. **Liabilities and Indemnities** – Risk and compensation responsibilities.
9. **Force Majeure** – Unforeseen protections.
10. **Amendments and Modifications** – How changes are handled.
11. **Warranties and Representations** – Performance and truth assurances.
12. **Governing Law** – Which jurisdiction governs the contract.
13. **Signatures and Dates** – Include signatories’ names and dates clearly.
14. **Annexures** – Brief all annexures or schedules (especially those with commercial terms).

Contract:
""" + full_text + "\n\nAnnexures:\n" + last_pages_text

    # Get summary from Together.ai (Mistral model)
    api_key = st.secrets["TOGETHER_API_KEY"]
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "max_tokens": 2048,
        "temperature": 0.4,
        "top_p": 0.9,
        "top_k": 50,
        "repetition_penalty": 1.1,
        "messages": [
            {"role": "system", "content": "You are a legal and commercial assistant. Provide summaries of contracts with both legal and business insights."},
            {"role": "user", "content": full_prompt}
        ]
    }

    with st.spinner("Analyzing contract and generating summary..."):
        response = requests.post("https://api.together.xyz/v1/chat/completions", headers=headers, json=payload)
        if response.status_code == 200:
            result = response.json()
            summary = result["choices"][0]["message"]["content"]
            st.subheader("📋 Contract Summary")
            st.markdown(summary)
        else:
            st.error(f"Failed to generate summary. Status Code: {response.status_code}\n{response.text}")
