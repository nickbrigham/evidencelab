"""
EvidenceLab - Evidence-Based Peptide & HRT Research Assistant
"""
import streamlit as st
import os
from config import APP_NAME, APP_DESCRIPTION, COMPOUND_CATEGORIES, RESPONSE_TARGETS
from utils.query_classifier import classify_query, get_query_context
from utils.perplexity_client import PerplexityClient
from utils.prompts import MEDICAL_DISCLAIMER

st.set_page_config(page_title=APP_NAME, page_icon="🧬", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .main > div { padding-top: 2rem; }
    
    /* Force black text everywhere */
    * { color: #000000; }
    .stChatMessage, .stChatMessage p, .stChatMessage li, .stChatMessage span, .stChatMessage div {
        color: #000000 !important;
        background-color: #f8f9fa !important;
    }
    .stChatMessage { 
        border-radius: 10px; 
        padding: 1rem; 
        margin-bottom: 1rem; 
    }
    [data-testid="stChatMessage"] * {
        color: #000000 !important;
    }
    
    /* Custom input box styling */
    .input-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: #ffffff;
        padding: 20px;
        border-top: 2px solid #1565c0;
        z-index: 1000;
    }
    .stTextArea textarea {
        min-height: 80px !important;
        font-size: 18px !important;
        color: #000000 !important;
        background-color: #ffffff !important;
        border: 2px solid #1565c0 !important;
        border-radius: 10px !important;
        padding: 15px !important;
    }
    .stTextArea label {
        color: #000000 !important;
        font-size: 16px !important;
    }
    
    /* Add padding at bottom for fixed input */
    .main .block-container {
        padding-bottom: 180px !important;
    }
    
    .query-badge { display: inline-block; padding: 0.25rem 0.75rem; background-color: #e3f2fd; color: #1565c0 !important; border-radius: 20px; font-size: 0.8rem; font-weight: 500; margin-bottom: 0.5rem; }
    .compound-tag { display: inline-block; padding: 0.2rem 0.5rem; background-color: #e8f5e9; color: #2e7d32 !important; border-radius: 4px; font-size: 0.75rem; margin-right: 0.25rem; }
    .disclaimer-box { background-color: #fff3e0; border-left: 4px solid #ff9800; padding: 1rem; margin: 1rem 0; border-radius: 4px; color: #000000 !important; }
    .disclaimer-box * { color: #000000 !important; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Mobile styles */
    @media (max-width: 768px) {
        [data-testid="collapsedControl"] { background-color: #1565c0 !important; border-radius: 8px !important; padding: 8px !important; }
        [data-testid="collapsedControl"] svg { stroke: white !important; width: 24px !important; height: 24px !important; }
        .mobile-menu-hint { display: block !important; background-color: #1565c0; color: white !important; padding: 0.75rem 1rem; border-radius: 8px; margin-bottom: 1rem; text-align: center; font-weight: 500; }
        
        .stTextArea textarea {
            min-height: 100px !important;
            font-size: 20px !important;
        }
        
        .main .block-container {
            padding-bottom: 220px !important;
        }
    }
    @media (min-width: 769px) { .mobile-menu-hint { display: none !important; } }
</style>
""", unsafe_allow_html=True)


def get_api_key():
    try:
        return st.secrets["PERPLEXITY_API_KEY"]
    except Exception:
        pass
    return os.getenv("PERPLEXITY_API_KEY")


def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "pending_query" not in st.session_state:
        st.session_state.pending_query = None
    if "perplexity_client" not in st.session_state:
        api_key = get_api_key()
        if api_key:
            try:
                st.session_state.perplexity_client = PerplexityClient(api_key)
                st.session_state.api_key_set = True
            except Exception:
                st.session_state.perplexity_client = None
                st.session_state.api_key_set = False
        else:
            st.session_state.perplexity_client = None
            st.session_state.api_key_set = False


def render_sidebar():
    with st.sidebar:
        st.image("https://em-content.zobj.net/source/apple/391/dna_1f9ec.png", width=60)
        st.title(APP_NAME)
        st.caption(APP_DESCRIPTION)
        st.divider()
        st.subheader("🔑 API Status")
        if st.session_state.api_key_set:
            st.success("✅ Connected")
        else:
            st.error("❌ API key not configured")
        st.divider()
        st.subheader("🧪 Quick Compound Lookup")
        category = st.selectbox("Category", options=list(COMPOUND_CATEGORIES.keys()), format_func=lambda x: x.title())
        compound = st.selectbox("Compound", options=COMPOUND_CATEGORIES[category])
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 TLDR", use_container_width=True):
                st.session_state.pending_query = f"Give me the TLDR on {compound}"
        with col2:
            if st.button("📊 Overview", use_container_width=True):
                st.session_state.pending_query = f"What is {compound}?"
        col3, col4 = st.columns(2)
        with col3:
            if st.button("💉 Dosage", use_container_width=True):
                st.session_state.pending_query = f"What's the dosage for {compound}?"
        with col4:
            if st.button("⏱️ Timeline", use_container_width=True):
                st.session_state.pending_query = f"When will I see results from {compound}?"
        col5, col6 = st.columns(2)
        with col5:
            if st.button("✅ Benefits", use_container_width=True):
                st.session_state.pending_query = f"What are the benefits of {compound}?"
        with col6:
            if st.button("⚠️ Side Effects", use_container_width=True):
                st.session_state.pending_query = f"What are the side effects of {compound}?"
        st.divider()
        with st.expander("📖 Response Types"):
            for qtype, info in RESPONSE_TARGETS.items():
                st.markdown(f"**{qtype.title()}**: {info['description']}")
        st.divider()
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        st.divider()
        st.caption("⚠️ Not medical advice. Consult a healthcare provider.")


def render_message(message):
    with st.chat_message(message["role"]):
        if message["role"] == "assistant" and "metadata" in message:
            meta = message["metadata"]
            cols = st.columns([1, 4])
            with cols[0]:
                st.markdown(f'<span class="query-badge">{meta.get("query_type", "overview").title()}</span>', unsafe_allow_html=True)
            with cols[1]:
                if meta.get("compounds"):
                    compound_tags = " ".join([f'<span class="compound-tag">{c}</span>' for c in meta["compounds"]])
                    st.markdown(compound_tags, unsafe_allow_html=True)
        st.markdown(message["content"])


def generate_response(prompt):
    st.session_state.messages.append({"role": "user", "content": prompt})
    query_type, compounds, confidence = classify_query(prompt)
    with st.chat_message("assistant"):
        status_cols = st.columns([2, 3])
        with status_cols[0]:
            st.caption(f"📝 Response type: **{query_type.title()}**")
        with status_cols[1]:
            if compounds:
                st.caption(f"🧪 Compounds: {', '.join(compounds)}")
        message_placeholder = st.empty()
        full_response = ""
        try:
            for chunk in st.session_state.perplexity_client.stream_query(user_message=prompt, query_type=query_type, compounds=compounds):
                full_response += chunk
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        except Exception as e:
            full_response = f"❌ Error: {str(e)}"
            message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response, "metadata": {"query_type": query_type, "compounds": compounds, "confidence": confidence}})


def main():
    init_session_state()
    render_sidebar()
    st.title("🧬 EvidenceLab")
    st.markdown("*Evidence-based peptide & HRT research assistant*")
    st.markdown('<div class="mobile-menu-hint">☰ Tap arrow in top-left for quick compound lookup</div>', unsafe_allow_html=True)
    st.markdown('<div class="disclaimer-box"><strong>⚠️ Important Disclaimer</strong><br>EvidenceLab provides educational information only. This is <strong>not medical advice</strong>. Always consult a qualified healthcare provider.</div>', unsafe_allow_html=True)
    if not st.session_state.api_key_set:
        st.error("⚠️ API not configured.")
        return
    
    # Display chat history
    for message in st.session_state.messages:
        render_message(message)
    
    # Handle pending query from sidebar
    if st.session_state.pending_query:
        prompt = st.session_state.pending_query
        st.session_state.pending_query = None
        generate_response(prompt)
        st.rerun()
    
    # Input area using text_area + button (more controllable than chat_input)
    st.divider()
    user_input = st.text_area(
        "Your question:",
        placeholder="Ask about peptides, hormones, or therapeutic compounds...",
        height=100,
        key="user_input"
    )
    
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        send_clicked = st.button("🚀 Send", use_container_width=True, type="primary")
    with col2:
        clear_input = st.button("Clear", use_container_width=True)
    
    if send_clicked and user_input.strip():
        generate_response(user_input.strip())
        st.rerun()


if __name__ == "__main__":
    main()
