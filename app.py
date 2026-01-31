import streamlit as st
from PyPDF2 import PdfReader
import google.generativeai as genai

# 1. Setup your Gemini API Key
# This pulls the key from your secrets.toml (local) or Streamlit Cloud (online)
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

def extract_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def main():
    st.set_page_config(page_title="AI Doc Assistant")
    st.header("Chat with your Business Reports 📄")

    # Sidebar for uploading
    with st.sidebar:
        st.title("Menu:")
        pdf_docs = st.file_uploader("Upload your PDF Files", accept_multiple_files=True)
        if st.button("Process"):
            with st.spinner("Analyzing..."):
                raw_text = extract_text(pdf_docs)
                st.session_state.raw_text = raw_text
                st.success("Done!")

    # Chat interface
    user_question = st.text_input("Ask a question about your document:")
    if user_question and "raw_text" in st.session_state:
        model = genai.GenerativeModel('gemini-1.5-flash')
        # We send the text + the question to the AI
        prompt = f"Context: {st.session_state.raw_text}\n\nQuestion: {user_question}"
        response = model.generate_content(prompt)
        st.write("AI Response:", response.text)

if __name__ == "__main__":
    main()
