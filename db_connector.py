# db_connector.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

def get_db_connection():
    """
    Koneksi ke PostgreSQL (Supabase) menggunakan DATABASE_URL
    """
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        st.error("❌ DATABASE_URL tidak ditemukan. Periksa Secrets di Streamlit Cloud.")
        st.stop()
    
    try:
        # Langsung gunakan DATABASE_URL, tanpa parameter terpisah
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        st.error(f"❌ Gagal konek ke database: {str(e)}")
        st.stop()

def get_schema_info():
    """Mengambil informasi schema database untuk konteks LLM"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Ambil daftar tabel (batasi 10 tabel utama)
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
        LIMIT 15
    """)
    tables = [row['table_name'] for row in cur.fetchall()]
    
    schema_info = []
    for table in tables:
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = %s AND table_schema = 'public'
            ORDER BY ordinal_position
        """, (table,))
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
        
        # Cek apakah query menghasilkan data (SELECT) atau hanya DML
        if cur.description:
            results = cur.fetchall()
            conn.commit()
            return {"success": True, "data": results, "row_count": len(results)}
        else:
            conn.commit()
            return {"success": True, "data": [], "row_count": cur.rowcount}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        cur.close()
        conn.close()