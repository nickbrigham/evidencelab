"""
Perplexity API Client for EvidenceLab
"""
from openai import OpenAI
from config import PERPLEXITY_API_KEY, PERPLEXITY_BASE_URL, PERPLEXITY_MODEL
from utils.prompts import SYSTEM_PROMPT, get_query_prompt, MEDICAL_DISCLAIMER


class PerplexityClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or PERPLEXITY_API_KEY
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY not set.")
        self.client = OpenAI(api_key=self.api_key, base_url=PERPLEXITY_BASE_URL)
        self.model = PERPLEXITY_MODEL
    
    def query(self, user_message, query_type="overview", compounds=None, include_citations=True, conversation_history=None):
        specific_prompt = get_query_prompt(query_type, user_message, compounds or [])
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": specific_prompt + "\n\n---\nOriginal question: " + user_message}
        ]
        try:
            response = self.client.chat.completions.create(model=self.model, messages=messages)
            content = response.choices[0].message.content
            content_with_disclaimer = content + MEDICAL_DISCLAIMER
            return {"content": content_with_disclaimer, "citations": [], "model": response.model, "query_type": query_type, "compounds": compounds}
        except Exception as e:
            return {"content": "Error: " + str(e), "citations": [], "model": None, "query_type": query_type, "compounds": compounds, "error": str(e)}
    
    def stream_query(self, user_message, query_type="overview", compounds=None, conversation_history=None):
        specific_prompt = get_query_prompt(query_type, user_message, compounds or [])
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": specific_prompt + "\n\n---\nOriginal question: " + user_message}
        ]
        try:
            stream = self.client.chat.completions.create(model=self.model, messages=messages, stream=True)
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
            yield MEDICAL_DISCLAIMER
        except Exception as e:
            yield "\n\nError: " + str(e)


def ask_evidencelab(question, query_type="overview"):
    client = PerplexityClient()
    from utils.query_classifier import classify_query
    detected_type, compounds, confidence = classify_query(question)
    final_type = query_type if query_type != "overview" else detected_type
    result = client.query(question, query_type=final_type, compounds=compounds)
    return result["content"]
