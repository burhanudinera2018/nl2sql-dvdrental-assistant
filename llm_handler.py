# llm_handler.py
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Konfigurasi Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# ← GUNAKAN MODEL YANG SUDAH TERBUKTI BERHASIL
MODEL_NAME = 'models/gemini-2.5-flash'

model = genai.GenerativeModel(MODEL_NAME)

def get_sql_from_natural_language(question, schema_info):
    """Mengubah pertanyaan natural language menjadi SQL query"""
    
    prompt = f"""
You are a PostgreSQL expert for a DVD rental database.

Database Schema (dvdrental):
{schema_info}

CRITICAL RULES:
1. Return ONLY the SQL query. NO explanations, NO markdown formatting.
2. Use PostgreSQL syntax.
3. Column names must match exactly as in schema.
4. For customer name, use first_name and last_name columns.
5. Always include LIMIT 10 for safety unless user specifies otherwise.
6. For "top" or "terbanyak" questions, use ORDER BY ... DESC.

Question: {question}

SQL Query:
"""
    
    try:
        response = model.generate_content(prompt)
        sql_query = response.text.strip()
        
        # Bersihkan hasil jika ada markdown
        if sql_query.startswith('```sql'):
            sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
        elif sql_query.startswith('```'):
            sql_query = sql_query.replace('```', '').strip()
        
        # Hapus kata "sql" di awal jika ada
        if sql_query.lower().startswith('sql'):
            sql_query = sql_query[3:].strip()
        
        return sql_query
    except Exception as e:
        return f"-- Error: {str(e)}"

def get_business_insight(question, sql_query, results):
    """Generate business insight dari hasil query"""
    
    # Batasi hasil yang dikirim ke LLM
    results_preview = results[:5] if results and len(results) > 5 else results
    
    prompt = f"""
Based on the following database query and results, provide a brief business insight (1-2 sentences).

Question: {question}
SQL Query: {sql_query}
Results (first {len(results_preview) if results_preview else 0} rows): {results_preview if results_preview else 'No results'}

Business Insight:
"""
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Insight: {len(results) if results else 0} rows found."