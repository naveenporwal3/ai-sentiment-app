import streamlit as st
from PyPDF2 import PdfReader
import google.generativeai as genai
from google.api_core import exceptions

# --------------------------------------------------
# 1. Page Configuration
# --------------------------------------------------
st.set_page_config(
    page_title="AI Doc Assistant",
    page_icon="✨",
    layout="wide"
)

# Advanced Decoration CSS
st.markdown("""
    <style>
    /* Main Background with soft gradient */
    .stApp { 
        background: linear-gradient(135deg, #fdfcfb 0%, #e2d1c3 100%); 
        background-attachment: fixed;
    }
    
    /* Remove unnecessary spacing */
    .block-container { padding-top: 1.5rem !important; }
    
    /* Sidebar Decor */
    section[data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.6) !important;
        backdrop-filter: blur(15px);
        border-right: 1px solid rgba(255,255,255,0.3);
    }

    /* Input Box Glowing Decoration */
    .stChatInputContainer {
        border-radius: 15px !important;
        border: 1px solid #6366f1 !important;
        box-shadow: 0 0 15px rgba(99, 102, 241, 0.1);
    }

    /* Button Decor */
    div.stButton > button:first-child {
        background: linear-gradient(to right, #6366f1, #a855f7);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 700;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(99, 102, 241, 0.4);
    }

    /* Status Text */
    .stAlert {
        border-radius: 12px;
        border: none;
    }
    
    /* Hide Default Elements */
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
    st.markdown("<h1 style='text-align: center; color: #4338ca;'>💼 DocAI</h1>", unsafe_allow_html=True)
    
    # Minimalist Uploader
    pdf_docs = st.file_uploader("Upload Company PDF", accept_multiple_files=True, label_visibility="collapsed")

    if st.button("✨ START ANALYSIS"):
        if not pdf_docs:
            st.warning("Please upload a file.")
        else:
            with st.spinner("Analyzing..."):
                raw_text = extract_text(pdf_docs)
                st.session_state.chunks = split_text(raw_text)
                st.session_state.messages = [] 
                st.success("Knowledge Synced!")

    # Decorative Process Image
    st.image("https://images.unsplash.com/photo-1620712943543-bcc4688e7485?auto=format&fit=crop&q=80&w=400", use_container_width=True)

    st.markdown("---")
    st.markdown(f"""
        <div style='background: white; padding: 15px; border-radius: 12px; border: 1px solid #eef2ff;'>
            <p style='margin:0; font-size: 12px; color: #64748b;'>DEVELOPER</p>
            <p style='margin:0; font-weight: bold; color: #1e293b;'>Naveen Porwal</p>
            <p style='margin-top: 5px; font-size: 11px;'>
                📧 <a href='mailto:naveenporwal3@hotmail.com' style='text-decoration:none; color:#6366f1;'>Email Me</a><br>
                🔗 <a href='https://www.linkedin.com/in/naveen-porwal/' style='text-decoration:none; color:#6366f1;'>LinkedIn</a>
            </p>
        </div>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# 5. Decorated Main Chat
# --------------------------------------------------
if "chunks" in st.session_state:
    st.markdown("<h3 style='margin-top: -10px;'>💬 Document Intelligence Chat</h3>", unsafe_allow_html=True)
    
    # Container for messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=message.get("avatar")):
            st.markdown(message["content"])

    if question := st.chat_input("Ask a professional question..."):
        st.session_state.messages.append({"role": "user", "content": question, "avatar": "👤"})
        with st.chat_message("user", avatar="👤"):
            st.markdown(question)

        context = " ".join(st.session_state.chunks[:4])
        prompt = f"Using context: {context}\n\nQuestion: {question}\n\nAnswer professionally:"

        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            with st.chat_message("assistant", avatar="🤖"):
                response = model.generate_content(prompt)
                answer = response.text
                st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer, "avatar": "🤖"})
        except Exception as e:
            st.error("Communication interrupted. Try again.")
else:
    # Decorated Welcome
    st.markdown("<h2 style='color:#4338ca;'>👋 Welcome to Smart Insights</h2>", unsafe_allow_html=True)
    st.info("I am ready to analyze your business documents. Please upload them in the sidebar to get started.")
    
    
    
    st.markdown("""
    **Workflow:**
    - **Step 1:** Upload PDFs (Financials, Reports, Contracts).
    - **Step 2:** Click **Start Analysis** to ingest data.
    - **Step 3:** Chat with the documents in real-time.
    """)
