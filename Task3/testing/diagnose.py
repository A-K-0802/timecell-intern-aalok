import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

def test_gemini_imports():
    """Test if we can import google.generativeai and check available attributes"""
    try:
        import google.generativeai as genai
        print("✓ google.generativeai imported successfully")
        
        # Check for configure function
        if hasattr(genai, 'configure'):
            print("✓ genai.configure() is available")
        else:
            print("✗ genai.configure() NOT found")
            
        # Check version
        if hasattr(genai, '__version__'):
            print(f"Version: {genai.__version__}")
        
        # Check for GenerativeModel
        if hasattr(genai, 'GenerativeModel'):
            print("✓ genai.GenerativeModel is available")
        else:
            print("✗ genai.GenerativeModel NOT found")
            
        # Check main classes and functions
        print("\nKey attributes in genai:")
        key_attrs = ['configure', 'GenerativeModel', 'types', 'Client', '__version__']
        for attr in key_attrs:
            status = "✓" if hasattr(genai, attr) else "✗"
            print(f"  {status} {attr}")
            
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    test_gemini_imports()
