import streamlit as st
import PyPDF2
import tempfile
import os
from together import Together

# Set page config
st.set_page_config(page_title="OnePageNote - Contract Summary", layout="wide")
st.title("📄 OnePageNote - Contract Analyzer")
st.write("Upload a contract, and get a complete legal + commercial summary in one page.")

# Upload PDF file
uploaded_file = st.file_uploader("Upload your contract (PDF only)", type="pdf")

if uploaded_file is not None:
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    # Extract text from PDF
    text = ""
    with open(tmp_path, "rb") as f:
        pdf_reader = PyPDF2.PdfReader(f)
        for page in pdf_reader.pages:
            text += page.extract_text() or ""

    os.remove(tmp_path)  # Delete temp file

    # Prepare summary prompt
    summary_prompt = f"""
You are a legal and commercial analyst. Summarize the contract clearly in one page with the following sections:

1. **Parties Involved**: Names and addresses of both parties.
2. **Purpose**: What this contract is about.
3. **Key Deliverables and Services**: Major outputs or responsibilities.
4. **Terms & Duration**: Start/end dates, renewal terms.
5. **Commercials**:
   - Total contract value, if mentioned.
   - Payment terms and frequency.
   - Taxes, discounts, escalation clauses.
   - Milestones and penalties/incentives.
6. **Obligations**: Duties of each party.
7. **SLAs & Performance Metrics**: Quality benchmarks or delivery KPIs.
8. **Termination Clause**: Exit terms and notice periods.
9. **Confidentiality & IP**: What information must be protected.
10. **Dispute Resolution**: How conflicts are to be resolved.
11. **Force Majeure**: Unforeseen events handling.
12. **Amendments**: How modifications are made.
13. **Governing Law**: Jurisdiction for legal matters.
14. **Signatures & Dates**: Names and dates of signatories.
15. **Annexures**: Clearly mention and copy full annexures attached at the end of the document.

Keep it concise but complete. Avoid generic legal filler. Focus on key commercial, financial, and operational terms.
"""

    # Generate summary using Together API
    with st.spinner("Analyzing contract and generating summary..."):
        client = Together(api_key=st.secrets["TOGETHER_API_KEY"])
        response = client.chat.completions.create(
            model="meta-llama/Llama-3-70b-chat-hf",
            messages=[
                {"role": "system", "content": "You are an expert legal and business assistant."},
                {"role": "user", "content": summary_prompt + "\n\nContract Text:\n" + text}
            ],
            temperature=0.3,
        )
        summary = response.choices[0].message.content

    st.subheader("📋 One Page Summary")
    st.markdown(summary)
