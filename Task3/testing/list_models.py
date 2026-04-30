"""Check available Gemini models"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import GEMINI_API_KEY, GEMINI_MODEL

try:
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    
    print("Available models:")
    for model in genai.list_models():
        print(f"  - {model.name}")
        if hasattr(model, 'supported_generation_methods'):
            methods = model.supported_generation_methods
            print(f"    Methods: {methods}")
except Exception as e:
    print(f"Error: {e}")
