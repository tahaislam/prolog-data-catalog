#!/usr/bin/env python3
"""
Ollama Setup Checker
Quick diagnostic to see if AI mode will work
"""

import requests
import sys

def check_ollama():
    """Check Ollama installation and setup"""
    
    print("🔍 Checking Ollama Setup...\n")
    
    # Check 1: Is Ollama running?
    print("1️⃣ Checking if Ollama is running...")
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=2)
        if response.status_code == 200:
            print("   ✅ Ollama is running!\n")
        else:
            print("   ❌ Ollama responded but with error")
            print("   Fix: Check Ollama service")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Ollama is NOT running")
        print("   Fix:")
        print("      Install: https://ollama.ai")
        print("      Start: ollama serve")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Check 2: Are models installed?
    print("2️⃣ Checking installed models...")
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=2)
        models = response.json().get('models', [])
        
        if not models:
            print("   ❌ NO MODELS INSTALLED!")
            print("   Fix:")
            print("      ollama pull llama3.2")
            print("      (This will download ~2GB)")
            return False
        
        print(f"   ✅ Found {len(models)} model(s):\n")
        for model in models:
            name = model.get('name', 'Unknown')
            size_bytes = model.get('size', 0)
            size_gb = size_bytes / (1024**3)
            print(f"      • {name} ({size_gb:.1f} GB)")
        
        print()
        
    except Exception as e:
        print(f"   ❌ Error checking models: {e}")
        return False
    
    # Check 3: Is a compatible model installed?
    print("3️⃣ Checking for compatible models...")
    model_names = [m.get('name', '') for m in models]
    
    has_llama32 = any('llama3.2' in name for name in model_names)
    has_llama31 = any('llama3.1' in name for name in model_names)
    has_mistral = any('mistral' in name for name in model_names)
    
    if has_llama32:
        print("   ✅ llama3.2 found - PERFECT!")
        recommended_model = 'llama3.2'
    elif has_llama31:
        print("   ✅ llama3.1 found - Great!")
        recommended_model = 'llama3.1'
    elif has_mistral:
        print("   ✅ mistral found - Good!")
        recommended_model = 'mistral'
    else:
        print("   ⚠️  No recommended models found")
        print("   You have:", ', '.join([m.split(':')[0] for m in model_names[:3]]))
        print("   Recommended:")
        print("      ollama pull llama3.2")
        recommended_model = model_names[0].split(':')[0] if model_names else None
    
    print()
    
    # Check 4: Test the model
    if recommended_model:
        print(f"4️⃣ Testing {recommended_model}...")
        try:
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': recommended_model,
                    'prompt': 'Say "OK" if you can read this.',
                    'stream': False,
                    'options': {'num_predict': 10}
                },
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                output = result.get('response', '').strip()
                print(f"   ✅ Model works! (responded: '{output[:50]}')")
            else:
                print(f"   ❌ Model test failed (status {response.status_code})")
                return False
                
        except Exception as e:
            print(f"   ❌ Model test error: {e}")
            return False
    
    print("\n" + "="*60)
    print("🎉 SUCCESS! AI mode should work!")
    print("="*60)
    print("\nTry it:")
    print("  python nl_interface.py --ai \"Find Gold datasets with problems\"")
    print()
    return True

if __name__ == '__main__':
    success = check_ollama()
    sys.exit(0 if success else 1)
