"""
EvidenceLab - Evidence-Based Peptide & HRT Research Assistant
Built with Streamlit + Perplexity AI
"""
import streamlit as st
from config import APP_NAME, APP_DESCRIPTION, COMPOUND_CATEGORIES, RESPONSE_TARGETS
from utils.query_classifier import classify_query, get_query_context
from utils.perplexity_client import PerplexityClient
from utils.prompts import MEDICAL_DISCLAIMER

# Page config
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main container */
    .main > div {
        padding-top: 2rem;
    }
    
    /* Chat messages */
    .stChatMessage {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    /* Query type badge */
    .query-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        background-color: #e3f2fd;
        color: #1565c0;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    
    /* Compound tag */
    .compound-tag {
        display: inline-block;
        padding: 0.2rem 0.5rem;
        background-color: #e8f5e9;
        color: #2e7d32;
        border-radius: 4px;
        font-size: 0.75rem;
        margin-right: 0.25rem;
    }
    
    /* Disclaimer box */
    .disclaimer-box {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 4px;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        padding-top: 2rem;
    }
    
    /* Quick actions buttons */
    .stButton > button {
        width: 100%;
        margin-bottom: 0.5rem;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "perplexity_client" not in st.session_state:
        st.session_state.perplexity_client = None
    if "api_key_set" not in st.session_state:
        st.session_state.api_key_set = False


def render_sidebar():
    """Render the sidebar with settings and quick actions."""
    with st.sidebar:
        st.image("https://em-content.zobj.net/source/apple/391/dna_1f9ec.png", width=60)
        st.title(APP_NAME)
        st.caption(APP_DESCRIPTION)
        
        st.divider()
        
        # API Key input
        st.subheader("🔑 API Configuration")
        api_key = st.text_input(
            "Perplexity API Key",
            type="password",
            help="Get your API key from https://www.perplexity.ai/settings/api"
        )
        
        if api_key:
            try:
                st.session_state.perplexity_client = PerplexityClient(api_key)
                st.session_state.api_key_set = True
                st.success("✅ API key set!")
            except Exception as e:
                st.error(f"Invalid API key: {e}")
                st.session_state.api_key_set = False
        
        st.divider()
        
        # Quick compound selection
        st.subheader("🧪 Quick Compound Lookup")
        category = st.selectbox(
            "Category",
            options=list(COMPOUND_CATEGORIES.keys()),
            format_func=lambda x: x.title()
        )
        
        compound = st.selectbox(
            "Compound",
            options=COMPOUND_CATEGORIES[category]
        )
        
        # Quick action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 TLDR", use_container_width=True):
                add_quick_query(f"Give me the TLDR on {compound}")
        with col2:
            if st.button("📊 Overview", use_container_width=True):
                add_quick_query(f"What is {compound}?")
        
        col3, col4 = st.columns(2)
        with col3:
            if st.button("💉 Dosage", use_container_width=True):
                add_quick_query(f"What's the dosage for {compound}?")
        with col4:
            if st.button("⏱️ Timeline", use_container_width=True):
                add_quick_query(f"When will I see results from {compound}?")
        
        col5, col6 = st.columns(2)
        with col5:
            if st.button("✅ Benefits", use_container_width=True):
                add_quick_query(f"What are the benefits of {compound}?")
        with col6:
            if st.button("⚠️ Side Effects", use_container_width=True):
                add_quick_query(f"What are the side effects of {compound}?")
        
        st.divider()
        
        # Response type info
        with st.expander("📖 Response Types"):
            for qtype, info in RESPONSE_TARGETS.items():
                st.markdown(f"**{qtype.title()}**: {info['description']} ({info['min']}-{info['max']} words)")
        
        st.divider()
        
        # Clear chat button
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        
        # Footer
        st.divider()
        st.caption("Built with ❤️ for evidence-based health research")
        st.caption("⚠️ Not medical advice. Consult a healthcare provider.")


def add_quick_query(query: str):
    """Add a quick query to the chat."""
    st.session_state.messages.append({"role": "user", "content": query})
    st.rerun()


def render_message(message: dict):
    """Render a single chat message with metadata."""
    with st.chat_message(message["role"]):
        # If assistant message, show query type badge
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


def render_disclaimer():
    """Render the medical disclaimer at the top of the chat."""
    st.markdown("""
    <div class="disclaimer-box">
        <strong>⚠️ Important Disclaimer</strong><br>
        EvidenceLab provides educational information only. This is <strong>not medical advice</strong>. 
        Always consult a qualified healthcare provider before starting any supplement, medication, or treatment.
        Many compounds discussed may be research chemicals or used off-label.
    </div>
    """, unsafe_allow_html=True)


def main():
    """Main app function."""
    init_session_state()
    render_sidebar()
    
    # Main chat area
    st.title("🧬 EvidenceLab")
    st.markdown("*Evidence-based peptide & HRT research assistant*")
    
    render_disclaimer()
    
    # Check if API key is set
    if not st.session_state.api_key_set:
        st.info("👈 Enter your Perplexity API key in the sidebar to get started.")
        st.markdown("""
        ### Getting Started
        
        1. **Get a Perplexity API key** from [perplexity.ai/settings/api](https://www.perplexity.ai/settings/api)
        2. **Enter your API key** in the sidebar
        3. **Ask questions** about peptides, hormones, and therapeutic compounds
        
        ### Example Questions
        
        - "What is BPC-157 and what does it do?"
        - "Give me the TLDR on testosterone replacement therapy"
        - "Compare BPC-157 vs TB-500 for injury healing"
        - "What's the dosage protocol for Ipamorelin?"
        - "When will I see results from CJC-1295?"
        - "What are the side effects of MK-677?"
        """)
        return
    
    # Display chat history
    for message in st.session_state.messages:
        render_message(message)
    
    # Chat input
    if prompt := st.chat_input("Ask about peptides, hormones, or therapeutic compounds..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Classify query
        query_type, compounds, confidence = classify_query(prompt)
        query_context = get_query_context(query_type)
        
        # Generate response
        with st.chat_message("assistant"):
            # Show what type of response we're generating
            status_cols = st.columns([2, 3])
            with status_cols[0]:
                st.caption(f"📝 Response type: **{query_type.title()}**")
            with status_cols[1]:
                if compounds:
                    st.caption(f"🧪 Compounds: {', '.join(compounds)}")
            
            # Create placeholder for streaming response
            message_placeholder = st.empty()
            full_response = ""
            
            # Stream the response
            try:
                for chunk in st.session_state.perplexity_client.stream_query(
                    user_message=prompt,
                    query_type=query_type,
                    compounds=compounds,
                    conversation_history=[
                        {"role": m["role"], "content": m["content"]} 
                        for m in st.session_state.messages[:-1]  # Exclude current message
                    ][-10:]  # Keep last 10 messages for context
                ):
                    full_response += chunk
                    message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
                
            except Exception as e:
                full_response = f"❌ Error generating response: {str(e)}\n\nPlease check your API key and try again."
                message_placeholder.markdown(full_response)
        
        # Save assistant message with metadata
        st.session_state.messages.append({
            "role": "assistant",
            "content": full_response,
            "metadata": {
                "query_type": query_type,
                "compounds": compounds,
                "confidence": confidence
            }
        })


if __name__ == "__main__":
    main()
