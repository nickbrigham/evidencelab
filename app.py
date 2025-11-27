"""
EvidenceLab - Evidence-Based Peptide & HRT Research Assistant
"""
import streamlit as st
import os
from config import APP_NAME, APP_DESCRIPTION, COMPOUND_CATEGORIES, RESPONSE_TARGETS
from utils.query_classifier import classify_query, get_query_context
from utils.perplexity_client import PerplexityClient
from utils.prompts import MEDICAL_DISCLAIMER

st.set_page_config(page_title=APP_NAME, page_icon="🧬", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .disclaimer-box { background-color: #fff3e0; border-left: 4px solid #ff9800; padding: 1rem; margin: 1rem 0; border-radius: 4px; }
    
    /* Make chat input much more visible */
    [data-testid="stChatInput"] {
        background-color: #e3f2fd !important;
        border-radius: 15px !important;
        padding: 15px !important;
        margin-top: 20px !important;
        box-shadow: 0 4px 12px rgba(21, 101, 192, 0.3) !important;
    }
    [data-testid="stChatInput"] > div {
        border: 3px solid #1565c0 !important;
        border-radius: 12px !important;
        background-color: #ffffff !important;
    }
    [data-testid="stChatInput"] textarea {
        font-size: 18px !important;
    }
    [data-testid="stChatInput"] textarea::placeholder {
        color: #666666 !important;
        font-size: 16px !important;
    }
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


def render_message(message):
    with st.chat_message(message["role"]):
        if message["role"] == "assistant" and "metadata" in message:
            meta = message["metadata"]
            st.caption(f"📝 {meta.get('query_type', 'overview').title()} | 🧪 {', '.join(meta.get('compounds', []))}")
        st.markdown(message["content"])


def generate_response(prompt):
    st.session_state.messages.append({"role": "user", "content": prompt})
    query_type, compounds, confidence = classify_query(prompt)
    
    with st.chat_message("assistant"):
        st.caption(f"📝 {query_type.title()} | 🧪 {', '.join(compounds) if compounds else 'General'}")
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
    
    st.session_state.messages.append({"role": "assistant", "content": full_response, "metadata": {"query_type": query_type, "compounds": compounds}})


def main():
    init_session_state()
    
    st.title("🧬 EvidenceLab")
    st.markdown("*Evidence-based peptide & HRT research assistant*")
    st.markdown('<div class="disclaimer-box"><strong>⚠️ Disclaimer:</strong> Educational info only. Not medical advice. Consult a healthcare provider.</div>', unsafe_allow_html=True)
    
    if not st.session_state.api_key_set:
        st.error("⚠️ API not configured.")
        return
    
    # Quick lookup in main area with expander
    with st.expander("🧪 Quick Compound Lookup", expanded=len(st.session_state.messages) == 0):
        col_cat, col_comp = st.columns(2)
        with col_cat:
            category = st.selectbox("Category", options=list(COMPOUND_CATEGORIES.keys()), format_func=lambda x: x.title())
        with col_comp:
            compound = st.selectbox("Compound", options=COMPOUND_CATEGORIES[category])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📋 TLDR", use_container_width=True):
                st.session_state.pending_query = f"Give me the TLDR on {compound}"
        with col2:
            if st.button("📊 Overview", use_container_width=True):
                st.session_state.pending_query = f"What is {compound}?"
        with col3:
            if st.button("💉 Dosage", use_container_width=True):
                st.session_state.pending_query = f"What's the dosage for {compound}?"
        
        col4, col5, col6 = st.columns(3)
        with col4:
            if st.button("⏱️ Timeline", use_container_width=True):
                st.session_state.pending_query = f"When will I see results from {compound}?"
        with col5:
            if st.button("✅ Benefits", use_container_width=True):
                st.session_state.pending_query = f"What are the benefits of {compound}?"
        with col6:
            if st.button("⚠️ Side Effects", use_container_width=True):
                st.session_state.pending_query = f"What are the side effects of {compound}?"
    
    # Clear chat button
    if st.session_state.messages:
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()
    
    st.divider()
    
    # Display chat history
    for message in st.session_state.messages:
        render_message(message)
    
    # Handle pending query
    if st.session_state.pending_query:
        prompt = st.session_state.pending_query
        st.session_state.pending_query = None
        generate_response(prompt)
        st.rerun()
    
    # Chat input
    if prompt := st.chat_input("Ask about peptides, hormones, or compounds..."):
        generate_response(prompt)
        st.rerun()


if __name__ == "__main__":
    main()
