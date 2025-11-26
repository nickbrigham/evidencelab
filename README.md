# 🧬 EvidenceLab

Evidence-based peptide & HRT research assistant built with Streamlit + Perplexity AI.

## What It Does

EvidenceLab helps users research peptides, hormones, and therapeutic compounds with:

- **Smart Query Classification**: Automatically detects what type of question you're asking (dosage, timeline, benefits, etc.)
- **Focused Responses**: Returns the right depth of information based on your question
- **Research-Backed**: Uses Perplexity's sonar-pro model to search and cite current research
- **Medical Disclaimers**: Always reminds users to consult healthcare providers

## Query Types

| Type | Trigger Words | Response Length |
|------|--------------|-----------------|
| TLDR | "tldr", "quick summary", "brief" | 150-200 words |
| Overview | "what is", general questions | 200-250 words |
| Dosage | "dose", "how much", "protocol" | 50-60 words |
| Timeline | "how long", "when will", "results" | 50-70 words |
| Benefits | "benefits", "what does it do" | 70-100 words |
| Side Effects | "side effects", "risks" | 55-75 words |
| Safety | "safe", "contraindications" | 60-80 words |
| Comparison | "vs", "compare", "difference" | 110-150 words |
| How-To | "how to", "instructions" | 80-120 words |
| Evidence | "studies", "research", "does it work" | 75-100 words |

## Setup

### 1. Clone/Download

```bash
cd evidencelab
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Get Perplexity API Key

1. Go to [perplexity.ai/settings/api](https://www.perplexity.ai/settings/api)
2. Create an API key
3. Either add to `.env` file or enter in the app sidebar

### 4. Run the App

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## Project Structure

```
evidencelab/
├── app.py                    # Main Streamlit application
├── config.py                 # Configuration and compound lists
├── requirements.txt          # Python dependencies
├── .env.example             # Example environment file
├── README.md                # This file
└── utils/
    ├── __init__.py
    ├── query_classifier.py   # Intent detection logic
    ├── perplexity_client.py  # Perplexity API wrapper
    └── prompts.py            # System prompts and templates
```

## Usage Examples

**General Overview:**
```
What is BPC-157?
Tell me about testosterone replacement therapy
```

**Quick Summary:**
```
Give me the TLDR on Ipamorelin
Quick summary of MK-677
```

**Dosing Info:**
```
What's the dosage for BPC-157?
How much TB-500 should I take?
```

**Results Timeline:**
```
When will I see results from CJC-1295?
How long until testosterone therapy works?
```

**Comparisons:**
```
BPC-157 vs TB-500 for tendon healing
Compare Ipamorelin and Sermorelin
```

## Customization

### Adding Compounds

Edit `config.py` to add more compounds to the categories:

```python
COMPOUND_CATEGORIES = {
    "peptides": ["BPC-157", "TB-500", ...],
    "hormones": ["Testosterone", ...],
    "sarms": ["Ostarine", ...],
}
```

### Modifying Prompts

Edit `utils/prompts.py` to customize:
- System prompt behavior
- Response templates for each query type
- Medical disclaimer text

### Adjusting Response Lengths

Edit `config.py` `RESPONSE_TARGETS` to change word count targets:

```python
RESPONSE_TARGETS = {
    "tldr": {"min": 150, "max": 200, ...},
    ...
}
```

## Tech Stack

- **Frontend**: Streamlit
- **AI/Search**: Perplexity API (sonar-pro model)
- **Python**: 3.9+

## Important Disclaimer

⚠️ **EvidenceLab provides educational information only. This is NOT medical advice.**

- Always consult a qualified healthcare provider
- Many compounds discussed are research chemicals or used off-label
- Individual results vary significantly
- Do not make medical decisions based solely on this tool

## License

MIT License - Use freely, but remember the medical disclaimer applies to any derivative works.

---

Built with ❤️ for evidence-based health research
