import streamlit as st
from PyPDF2 import PdfReader
import google.generativeai as genai

# Page Configuration
st.set_page_config(page_title="AI Document Assistant", layout="wide")

# 1. API Configuration (Using Streamlit Secrets)
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Please set the GEMINI_API_KEY in Streamlit Secrets.")

def extract_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            content = page.extract_text()
            if content:
                text += content
    return text

# UI Layout
st.title("📄 Smart Document Assistant")
st.markdown("---")

# Sidebar for uploading files
with st.sidebar:
    st.header("Upload Section")
    pdf_docs = st.file_uploader("Upload Business Reports (PDF)", accept_multiple_files=True)
    
    if st.button("Analyze Documents"):
        if pdf_docs:
            with st.spinner("Processing text..."):
                raw_text = extract_text(pdf_docs)
                st.session_state.raw_text = raw_text
                st.success("Analysis Complete!")
        else:
            st.warning("Please upload a file first.")

# Main Chat Interface
if "raw_text" in st.session_state:
    user_question = st.text_input("Ask a question about your data:")
    
    if user_question:
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Professional Reporting Prompt
        full_prompt = f"""
        You are a Data Science Reporting Assistant. 
        Context from document: {st.session_state.raw_text}
        
        User Question: {user_question}
        
        Answer professionally based ONLY on the provided context.
        """
        
        with st.spinner("Generating insight..."):
            response = model.generate_content(full_prompt)
            st.info("Assistant Response:")
            st.write(response.text)
else:
    st.info("Upload a PDF in the sidebar to start the AI analysis.")
