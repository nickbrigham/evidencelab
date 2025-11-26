"""
Perplexity API Client for EvidenceLab
Uses Perplexity's sonar model for research queries with citations
"""
from openai import OpenAI
from config import PERPLEXITY_API_KEY, PERPLEXITY_BASE_URL, PERPLEXITY_MODEL
from utils.prompts import SYSTEM_PROMPT, get_query_prompt, MEDICAL_DISCLAIMER


class PerplexityClient:
    """Client for Perplexity API using OpenAI SDK."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or PERPLEXITY_API_KEY
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY not set. Add it to your .env file.")
        
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
        """
        Send a query to Perplexity and get a response.
        
        Args:
            user_message: The user's question
            query_type: Type of query (overview, dosage, etc.)
            compounds: List of compounds mentioned in query
            include_citations: Whether to request citations
            conversation_history: Previous messages for context
        
        Returns:
            dict with 'content', 'citations', and 'model' keys
        """
        # Build the specific prompt based on query type
        specific_prompt = get_query_prompt(query_type, user_message, compounds or [])
        
        # Build messages array
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        
        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add the current query with specific instructions
        messages.append({
            "role": "user",
            "content": f"{specific_prompt}\n\n---\nOriginal question: {user_message}"
        })
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
            
            content = response.choices[0].message.content
            
            # Add medical disclaimer
            content_with_disclaimer = content + MEDICAL_DISCLAIMER
            
            # Extract citations if available (Perplexity includes them in response)
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
        """Extract citation URLs from response content."""
        import re
        # Perplexity often includes citations in [1], [2] format with URLs
        # This extracts any URLs found in the response
        url_pattern = r'https?://[^\s\)\]<>\"\']+' 
        urls = re.findall(url_pattern, content)
        return list(set(urls))  # Remove duplicates
    
    def stream_query(
        self,
        user_message: str,
        query_type: str = "overview",
        compounds: list[str] = None,
        conversation_history: list[dict] = None
    ):
        """
        Stream a query response for real-time display.
        
        Yields:
            str chunks of the response
        """
        specific_prompt = get_query_prompt(query_type, user_message, compounds or [])
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        
        if conversation_history:
            messages.extend(conversation_history)
        
        messages.append({
            "role": "user", 
            "content": f"{specific_prompt}\n\n---\nOriginal question: {user_message}"
        })
        
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
            
            # Yield disclaimer at end
            yield MEDICAL_DISCLAIMER
            
        except Exception as e:
            yield f"\n\n❌ Error: {str(e)}"


# Convenience function for quick queries
def ask_evidencelab(question: str, query_type: str = "overview") -> str:
    """Quick function to ask EvidenceLab a question."""
    client = PerplexityClient()
    from utils.query_classifier import classify_query
    
    detected_type, compounds, confidence = classify_query(question)
    # Use provided type or detected type
    final_type = query_type if query_type != "overview" else detected_type
    
    result = client.query(question, query_type=final_type, compounds=compounds)
    return result["content"]


if __name__ == "__main__":
    # Test the client
    client = PerplexityClient()
    
    test_question = "What is BPC-157 and what does it do?"
    print(f"Testing with: {test_question}\n")
    
    result = client.query(test_question, query_type="overview", compounds=["BPC-157"])
    print(result["content"])
    print(f"\nCitations: {result['citations']}")
