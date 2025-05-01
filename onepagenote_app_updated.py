import streamlit as st
import os
import tempfile
import fitz  # PyMuPDF
import docx2txt
import together

st.set_page_config(page_title="OnePageNote - Contract Summarizer", layout="wide")
st.title("📄 OnePageNote - Contract Summarizer")

uploaded_file = st.file_uploader("Upload a contract file (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])

if uploaded_file:
    file_ext = uploaded_file.name.split(".")[-1].lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix="." + file_ext) as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    # Extract text based on file type
    if file_ext == "pdf":
        doc = fitz.open(tmp_path)
        full_text = "\n".join([page.get_text() for page in doc])
        total_pages = len(doc)
        annexure_text = "\n".join([doc[i].get_text() for i in range(total_pages - 5, total_pages)])
        main_text = "\n".join([doc[i].get_text() for i in range(total_pages - 5)])
    elif file_ext == "docx":
        full_text = docx2txt.process(tmp_path)
        split_index = int(len(full_text.split()) * 0.85)
        words = full_text.split()
        main_text = " ".join(words[:split_index])
        annexure_text = " ".join(words[split_index:])
    elif file_ext == "txt":
        with open(tmp_path, "r", encoding="utf-8") as f:
            full_text = f.read()
        split_index = int(len(full_text.split()) * 0.85)
        words = full_text.split()
        main_text = " ".join(words[:split_index])
        annexure_text = " ".join(words[split_index:])
    else:
        st.error("Unsupported file format.")
        st.stop()

    # Call Together API
    api_key = st.secrets["TOGETHER_API_KEY"]
    together.api_key = api_key

    prompt_main = f"""
You are a legal assistant. Summarize the following contract. Provide a one-page structured summary with the following sections:

1. Parties Involved
2. Purpose of the Contract
3. Terms and Conditions (Duration, Payment, Obligations)
4. Deliverables and Timelines
5. Termination Clause
6. Confidentiality Clause
7. Dispute Resolution
8. Liabilities and Indemnities
9. Force Majeure
10. Amendments and Modifications
11. Warranties and Representations
12. Governing Law

---

Contract Text:
{main_text}
"""

    prompt_annexure = f"""
You are a legal assistant. From the following contract text (typically the last few pages), extract:
1. Complete Annexures (as-is)
2. Signature Names and Dates (if available)

---

Text:
{annexure_text}
"""

    with st.spinner("Summarizing contract..."):
        try:
            main_response = together.Complete.create(
                model="mistralai/Mixtral-8x7B-Instruct-v0.1",
                prompt=prompt_main,
                max_tokens=1024,
                temperature=0.7,
                stop=["---"]
            )
            annexure_response = together.Complete.create(
                model="mistralai/Mixtral-8x7B-Instruct-v0.1",
                prompt=prompt_annexure,
                max_tokens=1024,
                temperature=0.7,
                stop=["---"]
            )

            main_summary = main_response["output"].strip()
            annexure_summary = annexure_response["output"].strip()

            st.subheader("📌 Contract Summary")
            st.markdown(main_summary)

            st.subheader("📎 Annexures & Signatures")
            st.markdown(annexure_summary)

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

    os.remove(tmp_path
