"""Direct test of the new llm_client with gemini-2.5-flash"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Reimport to get fresh config
import importlib
import config
importlib.reload(config)

from config import GEMINI_API_KEY, GEMINI_MODEL
from llm_client import call_gemini

print(f"Using model: {GEMINI_MODEL}")
print(f"API Key set: {bool(GEMINI_API_KEY)}")

try:
    print("\nTest 1: Simple greeting")
    response = call_gemini("Say hello")
    print(f"✓ Response: {response}")
    
    print("\nTest 2: Math question")
    response = call_gemini("What is 5 + 3?")
    print(f"✓ Response: {response}")
    
    print("\nTest 3: Portfolio analysis")
    prompt = """Analyze this portfolio:
    - Stocks: $5000 (60%)
    - Bonds: $2000 (40%)
    
    Is this Aggressive, Balanced, or Conservative?"""
    response = call_gemini(prompt)
    print(f"✓ Response: {response}")
    
    print("\n✓ All tests passed!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
