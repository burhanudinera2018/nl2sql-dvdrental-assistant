# db_connector.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """Membuat koneksi ke PostgreSQL database dvdrental"""
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        cursor_factory=RealDictCursor
    )

def get_schema_info():
    """Mengambil informasi schema database untuk konteks LLM"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Ambil daftar tabel
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    tables = [row['table_name'] for row in cur.fetchall()]
    
    schema_info = []
    for table in tables[:10]:  # Batasi 10 tabel dulu untuk konteks
        cur.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = '{table}'
            ORDER BY ordinal_position
        """)
        columns = [f"{row['column_name']} ({row['data_type']})" for row in cur.fetchall()]
        schema_info.append(f"Table: {table}\nColumns: {', '.join(columns)}")
    
    cur.close()
    conn.close()
    
    return "\n\n".join(schema_info)

def execute_query(sql_query):
    """Eksekusi SQL query dan return hasil"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute(sql_query)
        results = cur.fetchall()
        conn.commit()
        return {"success": True, "data": results, "row_count": len(results)}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        cur.close()
        conn.close()