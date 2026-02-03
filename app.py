import streamlit as st
from PyPDF2 import PdfReader
import google.generativeai as genai
from google.api_core import exceptions

# --------------------------------------------------
# 1. Page Configuration & Custom Branding
# --------------------------------------------------
st.set_page_config(
    page_title="Smart AI Document Assistant",
    page_icon="📄",
    layout="wide"
)

# Professional CSS for SaaS look and feel
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%);
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.4);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(0,0,0,0.05);
    }

    /* Button Styling */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
        color: white;
        border-radius: 10px;
        border: none;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
    }

    /* Badge Styling */
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: bold;
        margin-right: 8px;
        background: #e0e7ff;
        color: #4338ca;
    }
    </style>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# 2. Gemini Configuration
# --------------------------------------------------
if "api_keys" not in st.secrets or "google_api_key" not in st.secrets["api_keys"]:
    st.error("Gemini API key not configured in secrets.toml.")
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
# 4. Sidebar / Control Center & Contact
# --------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=80)
    st.title("Control Center")
    st.markdown("---")
    
    st.header("📂 Data Source")
    pdf_docs = st.file_uploader("Upload business PDFs", accept_multiple_files=True)

    if st.button("🚀 Process Knowledge Base"):
        if not pdf_docs:
            st.warning("Please upload a file first.")
        else:
            with st.spinner("Processing PDF Content..."):
                raw_text = extract_text(pdf_docs)
                st.session_state.chunks = split_text(raw_text)
                st.session_state.messages = [] 
                st.success("Knowledge Base Ready!")

    # Contact Information Section
    st.markdown("---")
    st.header("👨‍💻 Contact Me")
    st.markdown("""
        **Naveen Porwal** *Data Analyst* 📧 [naveenporwal3@hotmail.com](mailto:naveenporwal3@hotmail.com)  
        📞 +91 9250 933 584  
        📍 Bangalore, India  
        
        [**LinkedIn Profile**](https://www.linkedin.com/in/naveen-porwal/)
    """)

# --------------------------------------------------
# 5. Main UI Display
# --------------------------------------------------
st.markdown('<h1 style="color:#1e293b; margin-bottom:0;">📄 Smart AI Document Assistant</h1>', unsafe_allow_html=True)
st.markdown("""
    <div style="margin-bottom: 25px;">
        <span class="badge">GEMINI 1.5 FLASH</span>
        <span class="badge">RAG ARCHITECTURE</span>
        <span class="badge">SECURE ANALYSIS</span>
    </div>
    """, unsafe_allow_html=True)

if "chunks" in st.session_state:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=message.get("avatar")):
            st.markdown(message["content"])

    if question := st.chat_input("Ask a question about your documents..."):
        st.session_state.messages.append({"role": "user", "content": question, "avatar": "👤"})
        with st.chat_message("user", avatar="👤"):
            st.markdown(question)

        context = " ".join(st.session_state.chunks[:4])
        prompt = f"Use this context: {context}\nQuestion: {question}\nAnswer ONLY based on context:"

        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("Analyzing..."):
                    response = model.generate_content(prompt)
                    answer = response.text
                    st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer, "avatar": "🤖"})
        except exceptions.ResourceExhausted:
            st.error("⚠️ API Quota exhausted. Try again in 60s.")
        except Exception as e:
            st.error(f"⚠️ Error: {str(e)}")
else:
    st.markdown("---")
    st.info("👋 **Welcome!** Please upload your PDF documents in the sidebar to begin.")
    
    st.image(
        "https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&q=80&w=1000", 
        caption="AI-Powered Document Intelligence",
        use_container_width=True
    )
    
    
    
    st.markdown("""
        ### Quick Start Guide:
        1. **Upload**: Use the sidebar to upload business PDFs.
        2. **Process**: Click 'Process Knowledge Base' to index data.
        3. **Chat**: Ask specific questions to extract insights.
    """)

st.markdown("---")
st.caption("Naveen Porwal | Portfolio 2026 | Powered by Google Gemini")
