import streamlit as st
from PyPDF2 import PdfReader
import google.generativeai as genai

# -----------------------------------
# Page Config
# -----------------------------------
st.set_page_config(
    page_title="AI Document Assistant",
    layout="wide"
)

# -----------------------------------
# Gemini API Config
# -----------------------------------
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Please add GEMINI_API_KEY in Streamlit secrets.")
    st.stop()

# -----------------------------------
# Functions
# -----------------------------------
def extract_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        reader = PdfReader(pdf)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text


def split_text(text, chunk_size=2000, overlap=200):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


# -----------------------------------
# UI
# -----------------------------------
st.title("📄 Smart AI Document Assistant")
st.markdown("Upload PDF reports and ask business questions.")

# Sidebar
with st.sidebar:
    st.header("📂 Upload Documents")

    pdf_docs = st.file_uploader(
        "Upload PDF files",
        accept_multiple_files=True
    )

    if st.button("Analyze Documents"):
        if not pdf_docs:
            st.warning("Please upload at least one PDF.")
        else:
            with st.spinner("Reading documents..."):
                raw_text = extract_text(pdf_docs)
                chunks = split_text(raw_text)
                st.session_state.text_chunks = chunks
                st.success("Documents processed successfully!")

# -----------------------------------
# Chat Section
# -----------------------------------
if "text_chunks" in st.session_state:

    user_question = st.text_input("Ask a question from the document:")

    if user_question:
        model = genai.GenerativeModel("gemini-2.5-flash-lite")

        # use only limited chunks to avoid token issue
        context = " ".join(st.session_state.text_chunks[:3])

        prompt = f"""
You are a professional business reporting assistant.

Answer ONLY using the context below.
If information is not available, say "Not found in document".

Context:
{context}

Question:
{user_question}
"""

        with st.spinner("Generating response..."):
            response = model.generate_content(prompt)
            st.subheader("📊 AI Response")
            st.write(response.text)

else:
    st.info("Upload PDF documents from the sidebar to start.")
