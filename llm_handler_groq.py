# llm_handler_groq.py
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Inisialisasi Groq client
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

# Model yang tersedia di Groq (gratis):
# - 'llama3-70b-8192' (paling akurat, sedikit lebih lambat)
# - 'llama3-8b-8192' (lebih cepat, cukup akurat)
# - 'mixtral-8x7b-32768' (alternatif bagus)

MODEL_NAME = 'llama3-70b-8192'  # atau 'llama3-8b-8192'

def get_sql_from_natural_language(question, schema_info):
    """Mengubah pertanyaan natural language menjadi SQL query menggunakan Groq"""
    
    system_prompt = f"""You are a PostgreSQL expert for a DVD rental database.

Database Schema:
{schema_info}

Rules:
1. Return ONLY the SQL query, no explanations.
2. Use PostgreSQL syntax.
3. Column names must match exactly as in schema.
4. For customer name, use first_name and last_name columns.
5. Always include LIMIT 10 for safety unless specified.

Examples:
- "Tampilkan 5 customer dengan rental terbanyak" → 
  SELECT c.customer_id, c.first_name, COUNT(r.rental_id) as total_rental 
  FROM customer c JOIN rental r ON c.customer_id = r.customer_id 
  GROUP BY c.customer_id ORDER BY total_rental DESC LIMIT 5
"""
    
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Question: {question}\n\nSQL Query:"}
            ],
            temperature=0.1,  # Low temperature for more deterministic SQL
            max_tokens=500
        )
        
        sql_query = completion.choices[0].message.content.strip()
        
        # Bersihkan hasil
        if sql_query.startswith('```sql'):
            sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
        elif sql_query.startswith('```'):
            sql_query = sql_query.replace('```', '').strip()
        
        return sql_query
    except Exception as e:
        return f"-- Error: {str(e)}"

def get_business_insight(question, sql_query, results):
    """Generate business insight dari hasil query menggunakan Groq"""
    
    system_prompt = "You are a business analyst. Provide 1-2 sentence actionable insights."
    
    user_prompt = f"""Based on this query and results, give a brief business insight.

Question: {question}
SQL: {sql_query}
Results (first 10 rows): {results[:10] if results else 'No results'}

Insight:"""
    
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=150
        )
        
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Insight generation failed: {str(e)}"