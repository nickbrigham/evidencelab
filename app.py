"""
EvidenceLab - Evidence-Based Peptide & HRT Research Assistant
"""
import streamlit as st
import streamlit.components.v1 as components
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
    @media (max-width: 768px) {
        .mobile-menu-hint { display: block; background-color: #1565c0; color: white; padding: 0.75rem 1rem; border-radius: 8px; margin-bottom: 1rem; text-align: center; font-weight: 500; }
    }
    @media (min-width: 769px) { .mobile-menu-hint { display: none; } }
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
                st.rerun()
        with col2:
            if st.button("📊 Overview", use_container_width=True):
                st.session_state.pending_query = f"What is {compound}?"
                st.rerun()
        col3, col4 = st.columns(2)
        with col3:
            if st.button("💉 Dosage", use_container_width=True):
                st.session_state.pending_query = f"What's the dosage for {compound}?"
                st.rerun()
        with col4:
            if st.button("⏱️ Timeline", use_container_width=True):
                st.session_state.pending_query = f"When will I see results from {compound}?"
                st.rerun()
        col5, col6 = st.columns(2)
        with col5:
            if st.button("✅ Benefits", use_container_width=True):
                st.session_state.pending_query = f"What are the benefits of {compound}?"
                st.rerun()
        with col6:
            if st.button("⚠️ Side Effects", use_container_width=True):
                st.session_state.pending_query = f"What are the side effects of {compound}?"
                st.rerun()
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
    render_sidebar()
    
    st.title("🧬 EvidenceLab")
    st.markdown("*Evidence-based peptide & HRT research assistant*")
    st.markdown('<div class="mobile-menu-hint">☰ Tap arrow in top-left for compound lookup</div>', unsafe_allow_html=True)
    st.markdown('<div class="disclaimer-box"><strong>⚠️ Disclaimer:</strong> Educational info only. Not medical advice. Consult a healthcare provider.</div>', unsafe_allow_html=True)
    
    if not st.session_state.api_key_set:
        st.error("⚠️ API not configured.")
        return
    
    for message in st.session_state.messages:
        render_message(message)
    
    if st.session_state.pending_query:
        prompt = st.session_state.pending_query
        st.session_state.pending_query = None
        generate_response(prompt)
        st.rerun()
    
    if prompt := st.chat_input("Ask about peptides, hormones, or compounds..."):
        generate_response(prompt)
        st.rerun()


if __name__ == "__main__":
    main()
