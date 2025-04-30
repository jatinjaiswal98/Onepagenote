import streamlit as st
import openai
import PyPDF2
import docx

st.set_page_config(page_title="OnePageNote - Contract Summary", layout="wide")
st.title("📄 OnePageNote – AI Contract Summary")

# Load OpenAI API key
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Helper to extract text
def extract_text(file):
    text = ""
    if file.name.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() or ""
    elif file.name.endswith(".docx"):
        doc = docx.Document(file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    elif file.name.endswith(".txt"):
        text = file.read().decode("utf-8")
    return text

# Upload
uploaded_file = st.file_uploader("Upload Contract File (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])

if uploaded_file:
    with st.spinner("Reading contract..."):
        contract_text = extract_text(uploaded_file)

    if contract_text:
        st.success("Contract uploaded. Generating summary...")

        with st.spinner("Generating summary with AI..."):
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a legal assistant. Summarize contracts."},
                    {"role": "user", "content": f"Summarize this contract in one page, including key terms, obligations, parties, duration, annexures, and any notable clauses:\n\n{contract_text[:10000]}"}
                ],
                temperature=0.4
            )
            summary = response.choices[0].message.content
            st.subheader("📌 One Page Summary")
            st.markdown(summary)
    else:
        st.error("Could not extract text from the file.")