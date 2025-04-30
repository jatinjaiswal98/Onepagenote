import streamlit as st
import openai
import docx
import PyPDF2
import time

st.set_page_config(page_title="OnePageNote", layout="wide")
st.title("📄 OnePageNote - Contract Summarizer")

uploaded_file = st.file_uploader("Upload contract (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])

if uploaded_file:
    file_type = uploaded_file.name.split('.')[-1]
    
    if file_type == "pdf":
        reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
    elif file_type == "docx":
        doc = docx.Document(uploaded_file)
        text = "\n".join([para.text for para in doc.paragraphs])
    elif file_type == "txt":
        text = uploaded_file.read().decode("utf-8")
    else:
        st.error("Unsupported file type.")
        st.stop()

    st.subheader("Contract Summary")
    with st.spinner("Generating summary..."):
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

        summary = ""
        for attempt in range(3):
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a legal assistant. Summarize contracts."},
                        {"role": "user", "content": f"Summarize this contract in one page, including key terms, obligations, parties, duration, annexures, and any notable clauses:\n\n{text}"}
                    ]
                )
                summary = response.choices[0].message.content
                break
            except openai.RateLimitError:
                st.warning("Rate limit hit. Retrying in 10 seconds...")
                time.sleep(10)
            except Exception as e:
                st.error(f"Error: {e}")
                break

        if summary:
            st.success("Summary generated!")
            st.text_area("📋 Contract Summary", summary, height=400)
