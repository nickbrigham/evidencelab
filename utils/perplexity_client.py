"""
Perplexity API Client for EvidenceLab
"""
import requests
from urllib.parse import urlparse
from config import PERPLEXITY_API_KEY, PERPLEXITY_BASE_URL, PERPLEXITY_MODEL
from utils.prompts import SYSTEM_PROMPT, get_query_prompt, MEDICAL_DISCLAIMER


class PerplexityClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or PERPLEXITY_API_KEY
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY not set.")
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.model = PERPLEXITY_MODEL
    
    def shorten_url(self, url):
        """Extract domain name from URL for display."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            if domain.startswith("www."):
                domain = domain[4:]
            return domain
        except:
            return url
    
    def stream_query(self, user_message, query_type="overview", compounds=None, conversation_history=None):
        """Query Perplexity and return response with citations."""
        specific_prompt = get_query_prompt(query_type, user_message, compounds or [])
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": specific_prompt + "\n\n---\nOriginal question: " + user_message}
            ],
            "return_citations": True
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            content = data["choices"][0]["message"]["content"]
            
            # Yield content in chunks
            chunk_size = 30
            for i in range(0, len(content), chunk_size):
                yield content[i:i+chunk_size]
            
            # Debug: show all keys in response
            yield f"\n\n*[Debug: API keys: {list(data.keys())}]*"
            
            # Try different possible citation field names
            citations = data.get("citations", []) or data.get("sources", []) or data.get("references", [])
            
            if citations:
                yield "\n\n---\n\n**📚 Sources:**\n"
                for i, url in enumerate(citations, 1):
                    short_name = self.shorten_url(url)
                    yield f"\n[{i}] [{short_name}]({url})"
            else:
                yield "\n\n*[Debug: No citations found in response]*"
            
            yield MEDICAL_DISCLAIMER
            
        except Exception as e:
            yield f"\n\nError: {str(e)}"


def ask_evidencelab(question, query_type="overview"):
    client = PerplexityClient()
    from utils.query_classifier import classify_query
    detected_type, compounds, confidence = classify_query(question)
    final_type = query_type if query_type != "overview" else detected_type
    
    result = ""
    for chunk in client.stream_query(question, query_type=final_type, compounds=compounds):
        result += chunk
    return result
