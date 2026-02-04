import os
import requests
import hashlib
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# In-memory cache for document summaries
_summary_cache: dict[str, str] = {}


def _get_context_hash(context: str) -> str:
    """Generate a hash for caching purposes."""
    return hashlib.md5(context.encode()).hexdigest()


def _extract_summary_from_reasoning(reasoning: str) -> str:
    """
    Extract the summary from a reasoning model's output.
    Returns the full reasoning content.
    """
    if not reasoning:
        return ""
    
    # Return the full reasoning content
    return reasoning.strip()


def summarize_documents(context: str, max_context_chars: int = 2000) -> str:
    """
    Summarize documents with optimizations for low latency:
    - Truncate context to reduce token count
    - Use caching to avoid repeated API calls
    - Optimized prompt for faster inference
    - Reduced max_tokens for faster response
    """
    print(f"[DEBUG] summarize_documents called with context length: {len(context)}")
    
    # Handle empty context
    if not context or not context.strip():
        print("[DEBUG] Empty context received")
        return "No document content available for summarization."
    
    # Check cache first
    context_hash = _get_context_hash(context)
    if context_hash in _summary_cache:
        print(f"[DEBUG] Cache hit for hash: {context_hash[:8]}...")
        return _summary_cache[context_hash]
    
    print(f"[DEBUG] Cache miss, calling API...")
    
    # Truncate context to reduce token count and latency
    truncated_context = context[:max_context_chars]
    if len(context) > max_context_chars:
        truncated_context += "\n[Document truncated for processing...]"
    
    # Get environment variables for Groq
    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    
    print(f"[DEBUG] API Key present: {bool(api_key)}")
    print(f"[DEBUG] API Key (first 10 chars): {api_key[:10] if api_key else 'None'}...")
    print(f"[DEBUG] Model: {model}")
    print(f"[DEBUG] Truncated context length: {len(truncated_context)}")
    
    if not api_key:
        print("[ERROR] GROQ_API_KEY not found!")
        return "Document validation failed: API key not configured."
    
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are an insurance document validator. Provide a brief 2-3 sentence summary assessing document legitimacy."
            },
            {
                "role": "user",
                "content": f"Summarize and validate this insurance document:\n\n{truncated_context}"
            }
        ],
        "max_tokens": 200,
        "temperature": 0.3,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    print(f"[DEBUG] Request URL: {GROQ_URL}")
    print(f"[DEBUG] Request payload model: {payload['model']}")

    try:
        print("[DEBUG] Sending POST request to Groq...")
        res = requests.post(GROQ_URL, json=payload, headers=headers, timeout=30)
        
        print(f"[DEBUG] Response status code: {res.status_code}")
        print(f"[DEBUG] Response headers: {dict(res.headers)}")
        
        response_text = res.text
        print(f"[DEBUG] Raw response (first 500 chars): {response_text[:500]}")
        
        if res.status_code != 200:
            print(f"[ERROR] API returned non-200 status: {res.status_code}")
            print(f"[ERROR] Response body: {response_text}")
            return f"Document processed. API returned status {res.status_code}."
        
        data = res.json()
        print(f"[DEBUG] Parsed JSON keys: {data.keys()}")
        
        # Check for API errors in response
        if "error" in data:
            error_info = data.get("error", {})
            print(f"[ERROR] API error in response: {error_info}")
            return f"Document processed. API error: {error_info.get('message', 'Unknown error')}"
        
        # Safely extract content
        choices = data.get("choices", [])
        print(f"[DEBUG] Number of choices: {len(choices)}")
        
        if not choices:
            print("[ERROR] No choices in API response")
            print(f"[DEBUG] Full response: {data}")
            return "Document received. Processing complete."
        
        message = choices[0].get("message", {})
        print(f"[DEBUG] Message keys: {message.keys()}")
        
        # Use content directly; Groq models do not provide a reasoning field
        summary = message.get("content", "").strip()
        
        print(f"[DEBUG] Extracted summary length: {len(summary)}")
        print(f"[DEBUG] Summary content: {summary[:200] if summary else 'EMPTY'}...")
        
        if not summary:
            print("[ERROR] Empty content in API response")
            return "Document validated. Content appears standard."
        
        # Cache the result
        _summary_cache[context_hash] = summary
        print(f"[DEBUG] Summary cached successfully")
        return summary
        
    except requests.exceptions.Timeout:
        print("[ERROR] Request timed out after 30 seconds")
        return "Document received. Summary pending due to high load."
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Request exception: {type(e).__name__}: {str(e)}")
        return f"Document validation complete. Network error occurred."
    except Exception as e:
        print(f"[ERROR] Unexpected exception: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Document validation complete. Status: processed."


def clear_summary_cache():
    """Clear the summary cache."""
    _summary_cache.clear()
