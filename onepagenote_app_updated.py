import streamlit as st
import os
import tempfile
from PyPDF2 import PdfReader
from docx import Document
import re
import openai

st.set_page_config(page_title="OnePageNote - Contract Summarizer")
st.title("📄 OnePageNote: AI Contract Summarizer")

uploaded_file = st.file_uploader("Upload a contract (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix="." + uploaded_file.name.split(".")[-1]) as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    file_text = ""

    if uploaded_file.name.endswith(".pdf"):
        reader = PdfReader(tmp_path)
        file_text = "\n".join([page.extract_text() for page in reader if page.extract_text()])
    elif uploaded_file.name.endswith(".docx"):
        doc = Document(tmp_path)
        file_text = "\n".join([para.text for para in doc.paragraphs])
    elif uploaded_file.name.endswith(".txt"):
        with open(tmp_path, "r", encoding="utf-8") as f:
            file_text = f.read()

    # Extract Annexure Pages (last 3 pages for safety)
    annexure_text = ""
    if uploaded_file.name.endswith(".pdf"):
        reader = PdfReader(tmp_path)
        annexure_text = "\n".join([reader.pages[i].extract_text() or "" for i in range(-3, 0)])

    full_prompt = f"""
    You are a legal and business analyst. Extract and summarize the following contract into one page. Include:

    🔹 Parties Involved
    🔹 Purpose of the Contract
    🔹 Terms and Conditions (duration, payments, obligations)
    🔹 Deliverables and Timelines
    🔹 Termination Clause
    🔹 Confidentiality
    🔹 Dispute Resolution
    🔹 Liabilities and Indemnities
    🔹 Force Majeure
    🔹 Amendments
    🔹 Warranties and Representations
    🔹 Governing Law
    🔹 Signatures and Dates
    🔹 Annexures (summarized + attach below if available)
    🔹 📌 Highlight any price or commercial figures (₹, INR, $, %, etc.)
    
    Contract:
    {file_text}
    """

    # Highlight price terms manually in original text for visibility
    highlighted_text = re.sub(r"(₹\s?\d+[\d,]*)", r"**\1**", file_text)
    highlighted_text = re.sub(r"\$\s?\d+[\d,]*", r"**\g<0>**", highlighted_text)
    highlighted_text = re.sub(r"\bINR\s?\d+[\d,]*", r"**\g<0>**", highlighted_text)

    from openai import OpenAI
    client = OpenAI(api_key=st.secrets["TOGETHER_API_KEY"])

    with st.spinner("Generating one-page summary..."):
        response = client.chat.completions.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            messages=[
                {"role": "system", "content": "You are a contract summarization assistant."},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.4
        )

        summary = response.choices[0].message.content

    st.subheader("📌 One Page Summary")
    st.markdown(summary)

    st.subheader("📎 Annexure (Extracted from contract)")
    st.text_area("Annexure Text", annexure_text, height=200)

    # Optionally download annexure text as a file
    st.download_button("📥 Download Annexure", annexure_text, file_name="Annexure.txt")

    st.subheader("🔍 Contract Text with Highlighted Commercial Terms")
    st.markdown(highlighted_text.replace("\n", "  \n"))
