import streamlit as st
from PyPDF2 import PdfReader
import google.generativeai as genai
from google.api_core import exceptions

# --------------------------------------------------
# 1. Page Configuration
# --------------------------------------------------
st.set_page_config(
    page_title="AI Doc Assistant",
    page_icon="📜",
    layout="wide"
)

# Deep Emerald & Golden Sands Decoration
st.markdown("""
    <style>
    /* Main Background: Soft Mint to White */
    .stApp { 
        background: linear-gradient(135deg, #f0fdf4 0%, #ffffff 100%); 
        background-attachment: fixed;
    }
    
    /* Global Text Color */
    html, body, [class*="st-"] { color: #064e3b; }

    /* Sidebar Decor: Deep Emerald */
    section[data-testid="stSidebar"] {
        background: rgba(6, 78, 59, 0.05) !important;
        backdrop-filter: blur(15px);
        border-right: 1px solid #d1fae5;
    }

    /* Input Box: Golden Border */
    .stChatInputContainer {
        border-radius: 12px !important;
        border: 2px solid #fbbf24 !important;
        background: white !important;
    }

    /* Button: Emerald Gradient */
    div.stButton > button:first-child {
        background: linear-gradient(to right, #059669, #10b981);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 700;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-thumb { background: #10b981; border-radius: 10px; }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# 2. Gemini Configuration
# --------------------------------------------------
if "api_keys" not in st.secrets or "google_api_key" not in st.secrets["api_keys"]:
    st.error("Missing API Key.")
    st.stop()

genai.configure(api_key=st.secrets["api_keys"]["google_api_key"])

# --------------------------------------------------
# 3. Core Logic
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
# 4. Decorated Sidebar
# --------------------------------------------------
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #065f46;'>🌿 DocInsight</h1>", unsafe_allow_html=True)
    
    pdf_docs = st.file_uploader("Upload PDF", accept_multiple_files=True, label_visibility="collapsed")

    if st.button("🔍 ANALYZE DOCUMENTS"):
        if not pdf_docs:
            st.warning("Please upload a file.")
        else:
            with st.spinner("Processing..."):
                raw_text = extract_text(pdf_docs)
                st.session_state.chunks = split_text(raw_text)
                st.session_state.messages = [] 
                st.success("Analysis Ready!")

    st.image("https://images.unsplash.com/photo-1507924538820-ede94a04019d?auto=format&fit=crop&q=80&w=400", use_container_width=True)

    st.markdown("---")
    st.markdown(f"""
        <div style='background: #ecfdf5; padding: 15px; border-radius: 12px; border: 1px solid #10b981;'>
            <p style='margin:0; font-size: 11px; color: #065f46; font-weight: bold;'>DEVELOPER</p>
            <p style='margin:0; font-size: 14px; color: #064e3b;'><b>Naveen Porwal</b></p>
            <p style='margin-top: 8px; font-size: 11px;'>
                📧 <a href='mailto:naveenporwal3@hotmail.com' style='color:#059669; text-decoration:none;'>Email</a> | 
                🔗 <a href='https://www.linkedin.com/in/naveen-porwal/' style='color:#059669; text-decoration:none;'>LinkedIn</a>
            </p>
        </div>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# 5. Main Chat Interface
# --------------------------------------------------
if "chunks" in st.session_state:
    st.markdown("<h3 style='color: #065f46;'>💬 Secure Document Chat</h3>", unsafe_allow_html=True)
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=message.get("avatar")):
            st.markdown(message["content"])

    if question := st.chat_input("Query your knowledge base..."):
        st.session_state.messages.append({"role": "user", "content": question, "avatar": "👤"})
        with st.chat_message("user", avatar="👤"):
            st.markdown(question)

        context = " ".join(st.session_state.chunks[:4])
        prompt = f"Using context: {context}\n\nQuestion: {question}\n\nAnswer concisely and professionally:"

        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            with st.chat_message("assistant", avatar="🌿"):
                response = model.generate_content(prompt)
                answer = response.text
                st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer, "avatar": "🌿"})
        except Exception:
            st.error("Server busy. Please retry.")
else:
    # Initial Landing
    st.markdown("<h2 style='color: #065f46;'>Ready to Analyze</h2>", unsafe_allow_html=True)
    st.write("Upload business reports or technical docs in the sidebar to extract intelligence using AI.")
    
        
    st.markdown("""
    **Getting Started:**
    1. Drag and drop your **PDF files** into the sidebar.
    2. Click **Analyze** to build the knowledge base.
    3. Type your questions in the chat box below.
    """)
