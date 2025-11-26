"""
EvidenceLab Configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_BASE_URL = "https://api.perplexity.ai"
PERPLEXITY_MODEL = "sonar-pro"  # Best for research queries with citations

# App Configuration
APP_NAME = "EvidenceLab"
APP_DESCRIPTION = "Evidence-based peptide & HRT research assistant"

# Response word count targets by query type
RESPONSE_TARGETS = {
    "overview": {"min": 200, "max": 250, "description": "Full compound overview"},
    "dosage": {"min": 40, "max": 60, "description": "Focused dosage info"},
    "timeline": {"min": 50, "max": 70, "description": "When results appear"},
    "benefits": {"min": 70, "max": 100, "description": "Primary benefits"},
    "side_effects": {"min": 55, "max": 75, "description": "Side effects"},
    "safety": {"min": 60, "max": 80, "description": "Safety profile"},
    "comparison": {"min": 110, "max": 150, "description": "Compare compounds"},
    "how_to": {"min": 80, "max": 120, "description": "Usage instructions"},
    "evidence": {"min": 75, "max": 100, "description": "Research quality"},
    "tldr": {"min": 150, "max": 200, "description": "Quick summary"},
}

# Compound categories
COMPOUND_CATEGORIES = {
    "peptides": [
        "BPC-157", "TB-500", "CJC-1295", "Ipamorelin", "Tesamorelin",
        "Sermorelin", "GHRP-6", "GHRP-2", "Hexarelin", "MK-677",
        "PT-141", "Melanotan II", "GHK-Cu", "Thymosin Alpha-1",
        "AOD-9604", "DSIP", "Epithalon", "Selank", "Semax",
        "LL-37", "KPV", "Dihexa", "PE-22-28"
    ],
    "hormones": [
        "Testosterone", "Testosterone Cypionate", "Testosterone Enanthate",
        "HCG", "Clomiphene", "Enclomiphene", "Anastrozole",
        "DHEA", "Pregnenolone", "Progesterone", "Estradiol",
        "Thyroid (T3/T4)", "Growth Hormone"
    ],
    "sarms": [
        "Ostarine (MK-2866)", "RAD-140", "LGD-4033", "S-4 (Andarine)",
        "YK-11", "Cardarine (GW-501516)", "SR9009"
    ]
}
