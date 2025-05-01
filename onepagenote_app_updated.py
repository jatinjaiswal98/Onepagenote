import streamlit as st
from PyPDF2 import PdfReader
import docx2txt
import tempfile
import re
import os
import base64
import requests

# Title
st.title("📄 OnePageNote - Contract Summarizer")

# Upload file
uploaded_file = st.file_uploader("Upload a contract", type=["pdf", "docx", "txt"])

file_text = ""
annexure_text = ""

# Extract text based on file type
if uploaded_file is not None:
    file_type = uploaded_file.name.split('.')[-1].lower()

    if file_type == "pdf":
        reader = PdfReader(uploaded_file)
        num_pages = len(reader.pages)
        file_text = "\n".join([page.extract_text() or "" for page in reader.pages])
        annexure_text = "\n".join([reader.pages[i].extract_text() or "" for i in range(max(num_pages - 5, 0), num_pages)])

    elif file_type == "docx":
        file_text = docx2txt.process(uploaded_file)
        annexure_text = "\n".join(file_text.splitlines()[-100:])  # last 100 lines as annexure

    elif file_type == "txt":
        content = uploaded_file.read().decode("utf-8")
        file_text = content
        annexure_text = "\n".join(content.splitlines()[-100:])  # last 100 lines as annexure

    else:
        st.error("Unsupported file format.")

    # Highlight pricing
    def highlight_prices(text):
        return re.sub(r'(\$\s?\d+[\d,\.]*|INR\s?\d+[\d,\.]*|Rs\.\s?\d+[\d,\.]*)', r'**\1**', text)

    file_text = highlight_prices(file_text)

    # Together.ai API setup
    api_key = st.secrets["TOGETHER_API_KEY"]
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    endpoint = "https://api.together.xyz/v1/chat/completions"

    # Prompt for detailed legal + commercial summary
    prompt = f"""
You are a contract analyst. Extract a detailed summary with the following points:
- Parties Involved
- Purpose of the Contract
- Terms and Conditions
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
- Commercials (prices, fees, payment terms)
- Annexure summary if available

Contract:
"""

    payload = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "messages": [
            {"role": "system", "content": "You are an expert contract summarizer."},
            {"role": "user", "content": prompt + file_text}
        ],
        "temperature": 0.4
    }

    # Generate summary
    with st.spinner("Analyzing contract and generating summary..."):
        res = requests.post(endpoint, headers=headers, json=payload)
        result = res.json()

    if 'choices' in result:
        summary = result['choices'][0]['message']['content']
        st.subheader("📋 Contract Summary")
        st.markdown(summary)

        # Show full annexure below summary
        st.subheader("📎 Annexure (Full Text)")
        st.text(annexure_text)

        # Offer annexure as downloadable attachment
        with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt') as annex_file:
            annex_file.write(annexure_text)
            st.download_button(
                label="Download Annexure",
                data=open(annex_file.name, 'rb').read(),
                file_name="Annexure.txt",
                mime="text/plain"
            )
    else:
        st.error("Something went wrong. Please try again later or check your API key usage.")
