"""
Test suite for Google Gemini API integration.
Validates API key, model availability, and basic functionality.
"""

import sys
import os

# Add parent directory to path to import from Task3
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import GEMINI_API_KEY, GEMINI_MODEL


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


def print_result(test_name, passed, message=""):
    """Print test result with color coding"""
    status = f"{Colors.GREEN}✓ PASS{Colors.END}" if passed else f"{Colors.RED}✗ FAIL{Colors.END}"
    print(f"[{status}] {test_name}")
    if message:
        print(f"      {Colors.BLUE}→ {message}{Colors.END}")


def test_1_library_import():
    """Test 1: Check if google-generativeai library is installed"""
    print(f"\n{Colors.YELLOW}Test 1: Library Import{Colors.END}")
    try:
        import google.generativeai as genai
        print_result("google-generativeai import", True, "Library successfully imported")
        return True, genai
    except ImportError as e:
        print_result("google-generativeai import", False, f"Error: {str(e)}")
        return False, None


def test_2_api_key_check():
    """Test 2: Check if GEMINI_API_KEY environment variable is set"""
    print(f"\n{Colors.YELLOW}Test 2: API Key Configuration{Colors.END}")
    if GEMINI_API_KEY:
        masked_key = f"{GEMINI_API_KEY[:8]}...{GEMINI_API_KEY[-4:]}"
        print_result("API key is set", True, f"API Key found: {masked_key}")
        return True
    else:
        print_result("API key is set", False, "GEMINI_API_KEY environment variable not found")
        return False


def test_3_model_config():
    """Test 3: Check if GEMINI_MODEL is configured"""
    print(f"\n{Colors.YELLOW}Test 3: Model Configuration{Colors.END}")
    if GEMINI_MODEL:
        print_result("Model is configured", True, f"Model: {GEMINI_MODEL}")
        return True
    else:
        print_result("Model is configured", False, "GEMINI_MODEL not configured")
        return False


def test_4_api_configuration(genai):
    """Test 4: Configure the API with provided key"""
    print(f"\n{Colors.YELLOW}Test 4: API Configuration{Colors.END}")
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        print_result("API configuration", True, "API successfully configured")
        return True, genai
    except Exception as e:
        print_result("API configuration", False, f"Error: {str(e)}")
        return False, None


def test_5_simple_api_call(genai):
    """Test 5: Make a simple API call to verify connectivity"""
    print(f"\n{Colors.YELLOW}Test 5: Simple API Call{Colors.END}")
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        generation_config = genai.types.GenerationConfig(temperature=0.0)
        response = model.generate_content("Say 'Hello from Gemini API'", generation_config=generation_config)
        
        if hasattr(response, 'text') and response.text:
            print_result("Simple API call", True, f"Response received: {response.text[:60]}...")
            return True, response.text
        else:
            print_result("Simple API call", False, "Response received but no text content")
            return False, None
    except Exception as e:
        print_result("Simple API call", False, f"Error: {str(e)}")
        return False, None


def test_6_test_prompt(genai):
    """Test 6: Test with a portfolio-related prompt (Task3 specific)"""
    print(f"\n{Colors.YELLOW}Test 6: Portfolio Analysis Prompt{Colors.END}")
    
    test_prompt = """Analyze this simple portfolio briefly:
- Stock A: $1000 (Growth)
- Bond B: $500 (Fixed Income)

Provide a one-sentence verdict: Aggressive, Balanced, or Conservative."""
    
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        generation_config = genai.types.GenerationConfig(temperature=0.0)
        response = model.generate_content(test_prompt, generation_config=generation_config)
        
        if hasattr(response, 'text') and response.text:
            print_result("Portfolio prompt test", True, f"Response: {response.text[:100]}...")
            return True, response.text
        else:
            print_result("Portfolio prompt test", False, "No response text received")
            return False, None
    except Exception as e:
        print_result("Portfolio prompt test", False, f"Error: {str(e)}")
        return False, None


def test_7_temperature_config(genai):
    """Test 7: Test API call with temperature parameter"""
    print(f"\n{Colors.YELLOW}Test 7: Temperature Configuration{Colors.END}")
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        generation_config = genai.types.GenerationConfig(temperature=0.0)
        response = model.generate_content("What is 2+2?", generation_config=generation_config)
        
        if hasattr(response, 'text') and response.text:
            print_result("Temperature configuration", True, f"Response: {response.text}")
            return True
        else:
            print_result("Temperature configuration", False, "No response received")
            return False
    except Exception as e:
        print_result("Temperature configuration", False, f"Error: {str(e)}")
        return False


def run_all_tests():
    """Run all tests in sequence"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"  Google Gemini API Test Suite")
    print(f"{'='*60}{Colors.END}\n")
    
    results = {}
    
    # Test 1: Library import
    test_1_passed, genai = test_1_library_import()
    results['Library Import'] = test_1_passed
    
    if not test_1_passed:
        print(f"\n{Colors.RED}Cannot proceed. google-generativeai library not found.{Colors.END}")
        print("Install with: pip install google-generativeai")
        return results
    
    # Test 2: API Key Check
    test_2_passed = test_2_api_key_check()
    results['API Key Check'] = test_2_passed
    
    # Test 3: Model Configuration
    test_3_passed = test_3_model_config()
    results['Model Configuration'] = test_3_passed
    
    # Test 4: API Configuration
    test_4_result = test_4_api_configuration(genai)
    test_4_passed = test_4_result[0]
    genai_configured = test_4_result[1]
    results['API Configuration'] = test_4_passed
    
    if not test_4_passed or not genai_configured:
        print(f"\n{Colors.RED}Cannot proceed. API configuration failed.{Colors.END}")
        return results
    
    # Test 5: Simple API Call
    test_5_passed, response_5 = test_5_simple_api_call(genai_configured)
    results['Simple API Call'] = test_5_passed
    
    if test_5_passed:
        # Test 6: Portfolio Prompt
        test_6_passed, response_6 = test_6_test_prompt(genai_configured)
        results['Portfolio Prompt'] = test_6_passed
        
        # Test 7: Temperature Config
        test_7_passed = test_7_temperature_config(genai_configured)
        results['Temperature Config'] = test_7_passed
    
    # Summary
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"  Test Summary")
    print(f"{'='*60}{Colors.END}\n")
    
    passed_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    
    for test_name, passed in results.items():
        status = f"{Colors.GREEN}✓{Colors.END}" if passed else f"{Colors.RED}✗{Colors.END}"
        print(f"{status} {test_name}")
    
    print(f"\n{Colors.BLUE}Result: {passed_count}/{total_count} tests passed{Colors.END}")
    
    if passed_count == total_count:
        print(f"{Colors.GREEN}✓ All tests passed! API is working correctly.{Colors.END}\n")
    else:
        print(f"{Colors.RED}✗ Some tests failed. Please check the errors above.{Colors.END}\n")
    
    return results


if __name__ == "__main__":
    run_all_tests()
