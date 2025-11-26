"""
Perplexity API Client for EvidenceLab
"""
from openai import OpenAI
from config import PERPLEXITY_API_KEY, PERPLEXITY_BASE_URL, 
PERPLEXITY_MODEL
from utils.prompts import SYSTEM_PROMPT, get_query_prompt, 
MEDICAL_DISCLAIMER


class PerplexityClient:
    """Client for Perplexity API using OpenAI SDK."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or PERPLEXITY_API_KEY
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY not set.")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=PERPLEXITY_BASE_URL
        )
        self.model = PERPLEXITY_MODEL
    
    def query(
        self,
        user_message: str,
        query_type: str = "overview",
        compounds: list[str] = None,
        include_citations: bool = True,
        conversation_history: list[dict] = None
    ) -> dict:
        specific_prompt = get_query_prompt(query_type, user_message, 
compounds or [])
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": 
f"{specific_prompt}\n\n---\nOriginal question: {user_message}"}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
            
            content = response.choices[0].message.content
            content_with_disclaimer = content + MEDICAL_DISCLAIMER
            citations = self._extract_citations(content)
            
            return {
                "content": content_with_disclaimer,
                "citations": citations,
                "model": response.model,
                "query_type": query_type,
                "compounds": compounds
            }
            
        except Exception as e:
            return {
                "content": f"Error querying Perplexity: {str(e)}",
                "citations": [],
                "model": None,
                "query_type": query_type,
                "compounds": compounds,
                "error": str(e)
            }
    
    def _extract_citations(self, content: str) -> list[str]:
        import re
        url_pattern = r'https?://[^\s\)\]<>\"\']+' 
        urls = re.findall(url_pattern, content)
        return list(set(urls))
    
    def stream_query(
        self,
        user_message: str,
        query_type: str = "overview",
        compounds: list[str] = None,
        conversation_history: list[dict] = None
    ):
        """Stream a query response - ignores conversation history to avoid 
API errors."""
        specific_prompt = get_query_prompt(query_type, user_message, 
compounds or [])
        
        # Simple messages - no history to avoid alternation issues
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": 
f"{specific_prompt}\n\n---\nOriginal question: {user_message}"}
        ]
        
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
            
            yield MEDICAL_DISCLAIMER
            
        except Exception as e:
            yield f"\n\n❌ Error: {str(e)}"


def ask_evidencelab(question: str, query_type: str = "overview") -> str:
    client = PerplexityClient()
    from utils.query_classifier import classify_query
    
    detected_type, compounds, confidence = classify_query(question)
    final_type = query_type if query_type != "overview" else detected_type
    
    result = client.query(question, query_type=final_type, 
compounds=compounds)
    return result["content"]
