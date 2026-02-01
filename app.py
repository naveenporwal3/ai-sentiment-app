import streamlit as st
from PyPDF2 import PdfReader
from google import genai
from google.genai import errors

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------
st.set_page_config(
    page_title="AI Document Assistant",
    layout="wide"
)

# --------------------------------------------------
# Gemini API Configuration
# --------------------------------------------------
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Gemini API key is not configured.")
    st.stop()

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# --------------------------------------------------
# Utility Functions
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
st.caption("AI-powered business document insights using Google Gemini")

with st.sidebar:
    st.header("📂 Upload Documents")

    pdf_docs = st.file_uploader(
        "Upload PDF files",
        accept_multiple_files=True
    )

    if st.button("Analyze Documents"):
        if not pdf_docs:
            st.warning("Please upload at least one PDF file.")
        else:
            with st.spinner("Reading documents..."):
                raw_text = extract_text(pdf_docs)
                st.session_state.text_chunks = split_text(raw_text)
                st.success("Documents processed successfully!")

# --------------------------------------------------
# Chat Section
# --------------------------------------------------
if "text_chunks" in st.session_state:

    user_question = st.text_input("Ask a question from the document:")

    if user_question:

        # Limit context to avoid token and quota abuse
        context = " ".join(st.session_state.text_chunks[:3])

        prompt = f"""
You are a professional business reporting assistant.

Answer ONLY using the context below.
If the answer is not available, say:
"Information not found in the document."

Context:
{context}

Question:
{user_question}
"""

        try:
            with st.spinner("Generating AI response..."):
                response = client.models.generate_content(
                    model="gemini-2.5-flash-lite",
                    contents=prompt
                )

                st.subheader("📊 AI Response")
                st.write(response.text)

        except errors.ResourceExhausted:
            st.warning(
                "⚠️ The AI service is temporarily busy due to high usage. "
                "Please wait a few seconds and try again."
            )

        except Exception:
            st.error(
                "⚠️ Something we
