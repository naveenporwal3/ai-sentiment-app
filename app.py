import streamlit as st
from PyPDF2 import PdfReader
import google.generativeai as genai
from google.api_core import exceptions

# --------------------------------------------------
# 1. Page Configuration
# --------------------------------------------------
st.set_page_config(
    page_title="AI Document Assistant",
    page_icon="📄",
    layout="wide"
)

# Optimized CSS for Single-Page View
st.markdown("""
    <style>
    .stApp { background: #f8fafc; }
    
    /* Tighten Header Spacing */
    .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.8);
        border-right: 1px solid #e2e8f0;
    }

    /* Button Styling */
    div.stButton > button:first-child {
        background: #6366f1;
        color: white;
        border-radius: 8px;
        font-weight: 600;
        width: 100%;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# 2. Gemini Configuration
# --------------------------------------------------
if "api_keys" not in st.secrets or "google_api_key" not in st.secrets["api_keys"]:
    st.error("API key not found.")
    st.stop()

genai.configure(api_key=st.secrets["api_keys"]["google_api_key"])

# --------------------------------------------------
# 3. Processing Logic
# --------------------------------------------------
def extract_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        reader = PdfReader(pdf)
        for page in reader.pages:
            content = page.extract_text()
            if content: text += content
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
# 4. Sidebar Control & Contact
# --------------------------------------------------
with st.sidebar:
    st.title("📄 Doc Assistant")
    
    pdf_docs = st.file_uploader("Upload PDF Documents", accept_multiple_files=True)

    if st.button("Analyze Data"):
        if not pdf_docs:
            st.warning("Upload a file.")
        else:
            with st.spinner("Processing..."):
                raw_text = extract_text(pdf_docs)
                st.session_state.chunks = split_text(raw_text)
                st.session_state.messages = [] 
                st.success("Ready!")

    # Moved Image to Sidebar to save space on main page
    st.image("https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&q=80&w=400", use_container_width=True)

    st.markdown("---")
    st.markdown("""
        **Naveen Porwal** 📧 [Email Me](mailto:naveenporwal3@hotmail.com)  
        🔗 [LinkedIn](https://www.linkedin.com/in/naveen-porwal/)
    """)

# --------------------------------------------------
# 5. Main UI
# --------------------------------------------------
st.subheader("Smart Document Chat")

if "chunks" in st.session_state:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Chat history container
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=message.get("avatar")):
            st.markdown(message["content"])

    if question := st.chat_input("Ask a question about your documents..."):
        st.session_state.messages.append({"role": "user", "content": question, "avatar": "👤"})
        with st.chat_message("user", avatar="👤"):
            st.markdown(question)

        context = " ".join(st.session_state.chunks[:4])
        prompt = f"Context: {context}\nQuestion: {question}\nAnswer using context only:"

        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            with st.chat_message("assistant", avatar="🤖"):
                response = model.generate_content(prompt)
                answer = response.text
                st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer, "avatar": "🤖"})
        except Exception as e:
            st.error("Error generating response.")
else:
    st.info("👋 **Welcome!** Upload PDFs in the sidebar to begin.")
    
    
    
    st.markdown("""
        **Quick Start:**
        1. Upload your files.
        2. Click 'Analyze Data'.
        3. Start chatting here.
    """)
