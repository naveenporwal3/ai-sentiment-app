import streamlit as st
from PyPDF2 import PdfReader
import google.generativeai as genai
from google.api_core import exceptions

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------
st.set_page_config(
    page_title="AI Document Assistant",
    layout="wide"
)

# --------------------------------------------------
# Gemini Configuration
# --------------------------------------------------
if "api_keys" not in st.secrets or "google_api_key" not in st.secrets["api_keys"]:
    st.error("Gemini API key not configured.")
    st.stop()

genai.configure(
    api_key=st.secrets["api_keys"]["google_api_key"]
)

# --------------------------------------------------
# Functions
# --------------------------------------------------
def extract_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        reader = PdfReader(pdf)
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content
    return text


def split_text(text, chunk_size=2000, overlap=200):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


# --------------------------------------------------
# UI
# --------------------------------------------------
st.title("📄 Smart AI Document Assistant")
st.caption("AI-powered business document insights using Gemini")

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
                st.session_state.chunks = split_text(raw_text)
                st.success("Documents processed successfully!")

# --------------------------------------------------
# Chat Section
# --------------------------------------------------
if "chunks" in st.session_state:

    question = st.text_input("Ask a question about the document:")

    if st.button("Get AI Answer"):

        context = " ".join(st.session_state.chunks[:3])

        prompt = f"""
You are a professional business reporting assistant.

Answer ONLY using the context below.
If information is not available, say:
"Information not found in the document."

Context:
{context}

Question:
{question}
"""

        try:
            model = genai.GenerativeModel("gemini-2.5-flash-lite")

            with st.spinner("Generating AI response..."):
                response = model.generate_content(prompt)

            st.subheader("📊 AI Response")
            st.write(response.text)

        except exceptions.ResourceExhausted:
            st.warning(
                "⚠️ Gemini free API quota reached. "
                "Please wait and try again later."
            )

        except Exception:
            st.error(
                "⚠️ Unable to generate response right now. Please try again later."
            )

else:
    st.info("Upload PDF documents from the sidebar to begin.")
