from typing import Optional
from config import GEMINI_API_KEY, GEMINI_MODEL


def call_gemini(prompt: str, model: Optional[str] = None, temperature: float = 0.0) -> str:
    """
    Call Google Gemini API with a prompt.
    
    Args:
        prompt: The prompt to send to Gemini
        model: Model name (defaults to GEMINI_MODEL from config)
        temperature: Temperature for generation (0.0 = deterministic)
    
    Returns:
        The text response from Gemini
    
    Raises:
        RuntimeError: If library not installed, API key not set, or API call fails
    """
    model = model or GEMINI_MODEL
    try:
        import google.generativeai as genai
    except ImportError as e:
        raise RuntimeError(
            "google-generativeai not installed. Install with: pip install google-generativeai"
        ) from e
    
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY not set in environment")
    
    # Configure API
    genai.configure(api_key=GEMINI_API_KEY)
    
    # Create generation config with temperature
    generation_config = genai.types.GenerationConfig(temperature=temperature)
    
    # Create model and generate response
    gen_model = genai.GenerativeModel(model)
    response = gen_model.generate_content(prompt, generation_config=generation_config)
    
    # Extract and return text
    return response.text
