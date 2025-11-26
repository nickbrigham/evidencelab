"""
Query Classifier - Detects user intent and routes to appropriate response type
"""
import re
from typing import Literal, Tuple
from config import COMPOUND_CATEGORIES

QueryType = Literal[
    "overview", "dosage", "timeline", "benefits", "side_effects",
    "safety", "comparison", "how_to", "evidence", "tldr"
]

# Keyword patterns for each query type (priority order matters)
QUERY_PATTERNS = {
    "tldr": [
        r"\btldr\b", r"\btl;dr\b", r"\bquick summary\b", r"\bshort version\b",
        r"\bbrief\b", r"\bnutshell\b", r"\bsummarize\b", r"\bquickly\b"
    ],
    "side_effects": [
        r"\bside effects?\b", r"\badverse\b", r"\bnegative effect\b", r"\bdanger\b",
        r"\brisks?\b", r"\bdownsides?\b", r"\bproblems?\b",
        r"\bconcerns?\b", r"\bharmful\b", r"\bbad effects?\b"
    ],
    "dosage": [
        r"\bdose\b", r"\bdosage\b", r"\bhow much\b", r"\bhow many\b",
        r"\bmg\b", r"\bmcg\b", r"\biu\b", r"\bprotocol\b", r"\bfrequency\b",
        r"\bhow often\b", r"\binjection\b", r"\badminister\b"
    ],
    "timeline": [
        r"\bhow long\b", r"\bwhen will\b", r"\bwhen do\b", r"\bresults\b",
        r"\bkick in\b", r"\bstart working\b", r"\bnotice\b", r"\bfeel\b",
        r"\btimeline\b", r"\bweeks?\b.*\bresults\b", r"\bdays?\b.*\bwork\b"
    ],
    "benefits": [
        r"\bbenefits?\b", r"\bwhat does.*do\b", r"\bhelp with\b", r"\bgood for\b",
        r"\bpros?\b", r"\badvantages?\b", r"\bimprove\b",
        r"\bwhy take\b", r"\bwhy use\b", r"\bpurpose\b"
    ],
    "safety": [
        r"\bsafe\b", r"\bsafety\b", r"\bdangerous\b",
        r"\bcontraindication\b", r"\binteraction\b", r"\bavoid\b",
        r"\bwarning\b", r"\bshould.*not\b", r"\bwho shouldn't\b"
    ],
    "comparison": [
        r"\bvs\.?\b", r"\bversus\b", r"\bcompare\b", r"\bdifference\b",
        r"\bbetter\b", r"\bworse\b", r"\bor\b.*\bwhich\b", r"\bchoose\b",
        r"\balternative\b", r"\binstead of\b"
    ],
    "how_to": [
        r"\bhow to\b", r"\bhow do i\b", r"\binstruction\b", r"\bstep\b",
        r"\breconstitute\b", r"\bmix\b", r"\bprepare\b", r"\bstore\b",
        r"\bsubcutaneous\b", r"\bintramuscular\b", r"\binject\b"
    ],
    "evidence": [
        r"\bstud(?:y|ies)\b", r"\bresearch\b", r"\bevidence\b", r"\bproven\b",
        r"\bscience\b", r"\btrial\b", r"\bpubmed\b", r"\bcitation\b",
        r"\bwork\b.*\breally\b", r"\bdoes it work\b", r"\blegit\b"
    ],
}


def extract_compounds(query: str) -> list[str]:
    """Extract compound names mentioned in the query."""
    query_lower = query.lower()
    found = []
    
    all_compounds = []
    for category_compounds in COMPOUND_CATEGORIES.values():
        all_compounds.extend(category_compounds)
    
    for compound in all_compounds:
        # Create flexible pattern for compound names
        pattern = compound.lower().replace("-", r"[\s\-]?").replace(" ", r"[\s\-]?")
        if re.search(pattern, query_lower):
            found.append(compound)
    
    return found


def classify_query(query: str) -> Tuple[QueryType, list[str], float]:
    """
    Classify user query into response type.
    
    Returns:
        Tuple of (query_type, compounds_mentioned, confidence_score)
    """
    query_lower = query.lower().strip()
    
    # Extract compounds mentioned
    compounds = extract_compounds(query)
    
    # Priority order for checking (some patterns can overlap)
    priority_order = [
        "tldr", "side_effects", "dosage", "timeline", "comparison",
        "how_to", "evidence", "safety", "benefits"
    ]
    
    # Score each query type
    scores = {}
    for query_type, patterns in QUERY_PATTERNS.items():
        score = 0
        for pattern in patterns:
            if re.search(pattern, query_lower, re.IGNORECASE):
                score += 1
        scores[query_type] = score
    
    # Find best match respecting priority for ties
    best_type = "overview"
    best_score = 0
    
    for query_type in priority_order:
        if scores.get(query_type, 0) > best_score:
            best_type = query_type
            best_score = scores[query_type]
    
    # Calculate confidence (0-1 scale)
    confidence = min(best_score / 3, 1.0) if best_score > 0 else 0.0
    
    # Default to overview if no strong match
    if best_score == 0:
        return "overview", compounds, 0.5
    
    return best_type, compounds, confidence


def get_query_context(query_type: QueryType) -> dict:
    """Get context info for the query type."""
    contexts = {
        "overview": {
            "focus": "comprehensive introduction",
            "include": ["what it is", "primary uses", "mechanism", "who uses it", "research status"],
            "tone": "educational, balanced"
        },
        "dosage": {
            "focus": "specific dosing protocols",
            "include": ["typical ranges", "frequency", "timing", "titration"],
            "tone": "precise, practical"
        },
        "timeline": {
            "focus": "when to expect results",
            "include": ["initial effects", "peak results", "duration", "individual variation"],
            "tone": "realistic, hopeful"
        },
        "benefits": {
            "focus": "positive effects and outcomes",
            "include": ["primary benefits", "secondary benefits", "research-backed claims"],
            "tone": "informative, not promotional"
        },
        "side_effects": {
            "focus": "potential negative effects",
            "include": ["common", "uncommon", "rare but serious", "management"],
            "tone": "honest, not alarmist"
        },
        "safety": {
            "focus": "safety profile and precautions",
            "include": ["contraindications", "interactions", "populations to avoid", "monitoring"],
            "tone": "cautious, thorough"
        },
        "comparison": {
            "focus": "differences between compounds",
            "include": ["mechanisms", "effectiveness", "side effects", "cost", "availability"],
            "tone": "objective, balanced"
        },
        "how_to": {
            "focus": "practical usage instructions",
            "include": ["preparation", "administration", "storage", "common mistakes"],
            "tone": "clear, step-by-step"
        },
        "evidence": {
            "focus": "research quality and status",
            "include": ["study types", "sample sizes", "limitations", "consensus"],
            "tone": "scientific, nuanced"
        },
        "tldr": {
            "focus": "quick actionable summary",
            "include": ["what it does", "who it's for", "key numbers", "verdict"],
            "tone": "direct, punchy"
        },
    }
    return contexts.get(query_type, contexts["overview"])


if __name__ == "__main__":
    # Test the classifier
    test_queries = [
        "What is BPC-157?",
        "How much BPC-157 should I take?",
        "When will I see results from TB-500?",
        "BPC-157 vs TB-500",
        "Is testosterone therapy safe?",
        "Give me the TLDR on Ipamorelin",
        "How to reconstitute peptides",
        "Does MK-677 actually work? Show me studies",
        "What are the benefits of CJC-1295?",
        "Side effects of testosterone cypionate"
    ]
    
    for query in test_queries:
        qtype, compounds, conf = classify_query(query)
        print(f"Query: {query}")
        print(f"  Type: {qtype}, Compounds: {compounds}, Confidence: {conf:.2f}")
        print()
