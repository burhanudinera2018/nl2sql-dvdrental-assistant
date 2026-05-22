import streamlit as st
import pandas as pd
from db_connector import get_schema_info, execute_query
from llm_handler import get_sql_from_natural_language, get_business_insight

st.set_page_config(page_title="DVD Rental AI Assistant", layout="wide")

# Header
st.title("🎬 DVD Rental AI Assistant")
st.markdown("Tanya dalam bahasa Indonesia atau Inggris, dapatkan hasil query SQL secara instan!")

# Sidebar
with st.sidebar:
    st.header("⚙️ Informasi")
    st.markdown("""
    **Database:** PostgreSQL `dvdrental`  
    **Tabel:** 16 tabel (customer, rental, film, payment, dll)  
    **Model:** Google Gemini 2.5 Flash  
    **Status:** 🟢 Live di Supabase Cloud
    """)
    
    if st.button("📊 Lihat Schema Database"):
        schema = get_schema_info()
        st.text_area("Schema:", schema, height=300)

# Main chat interface
st.header("💬 Natural Language Query")

# Inisialisasi session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Tampilkan history chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "sql" in msg:
            st.code(msg["sql"], language="sql")
        if "dataframe" in msg:
            st.dataframe(msg["dataframe"])

# Input user
question = st.chat_input("Tanyakan tentang data DVD rental...")

if question:
    # Tampilkan pertanyaan user
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    
    # Proses dengan LLM
    with st.chat_message("assistant"):
        with st.spinner("🔄 Menerjemahkan ke SQL..."):
            schema_info = get_schema_info()
            sql_query = get_sql_from_natural_language(question, schema_info)
        
        st.code(sql_query, language="sql")
        
        with st.spinner("🔄 Mengeksekusi query..."):
            result = execute_query(sql_query)
        
        if result["success"]:
            df = pd.DataFrame(result["data"])
            st.success(f"✅ {result['row_count']} baris ditemukan")
            st.dataframe(df)
            
            with st.spinner("🔄 Menghasilkan insight..."):
                insight = get_business_insight(question, sql_query, result["data"])
            
            st.info(f"💡 **Insight:** {insight}")
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": insight,
                "sql": sql_query,
                "dataframe": df
            })
        else:
            st.error(f"❌ Error: {result['error']}")
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Error: {result['error']}"
            })

# ============================================
# FOOTER - PROFESSIONAL CREDITS
# ============================================
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; padding: 20px; color: #666; font-size: 12px;">
        <p>
            🚀 <strong>Powered by Google Gemini AI</strong> &nbsp;|&nbsp; 
            🗄️ <strong>Database: PostgreSQL DVD Rental</strong> &nbsp;|&nbsp; 
            🎨 <strong>Built with Streamlit</strong>
        </p>
        <p>
            📅 © 2026 <strong>Burhanudin Badiuzaman</strong> — All Rights Reserved
        </p>
        <p style="font-size: 10px; color: #999;">
            Natural Language to SQL Assistant | Portfolio Project for Data Scientist (Google) | 
            <a href="https://github.com/burhanudin/nl2sql-dvdrental" target="_blank">GitHub Repository</a>
        </p>
    </div>
    """,
    unsafe_allow_html=True
)