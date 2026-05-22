# test_gemini.py
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Test dengan model yang berbeda
models_to_test = [
    'models/gemini-2.5-flash',
    'models/gemini-2.5-flash-lite', 
    'models/gemini-1.5-flash'
]

for model_name in models_to_test:
    print(f"\n🔍 Mencoba model: {model_name}")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say 'OK' in one word")
        print(f"   ✅ BERHASIL: {response.text}")
        print(f"   🎯 Gunakan model ini: {model_name}")
        break
    except Exception as e:
        if "429" in str(e):
            print(f"   ❌ Quota habis untuk model ini")
        else:
            print(f"   ❌ Error: {str(e)[:100]}")