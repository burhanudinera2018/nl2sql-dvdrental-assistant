# db_connector.py
"""
Koneksi database untuk NL2SQL DVD Rental Assistant.

Alur:
1. Setiap SQL dari LLM diperiksa dulu oleh is_safe_select(): hanya SELECT/WITH yang boleh jalan.
2. Query dijalankan di PostgreSQL (Supabase) dalam sesi READ ONLY.
3. Jika Supabase tidak bisa dihubungi (mis. proyek dijeda), query yang sama dijalankan
   di DuckDB terhadap snapshot Parquet di folder data_snapshot/.
4. Detail error hanya dicatat di log (Manage app), tidak ditampilkan ke pengunjung.

Membuat/memperbarui snapshot: python ekspor_snapshot.py  (lihat file tersebut)
"""
import os
import re
from pathlib import Path

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

SNAPSHOT_DIR = Path(__file__).resolve().parent / "data_snapshot"

FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|alter|truncate|create|grant|revoke|copy|merge|call|"
    r"execute|vacuum|comment|reindex|cluster|lock|attach|install|load|pragma|export)\b",
    re.IGNORECASE,
)


def _log(pesan):
    """Catat ke log Streamlit (terlihat di Manage app), bukan ke layar pengunjung."""
    print(f"[db_connector] {pesan}", flush=True)


def is_safe_select(sql):
    """True hanya untuk SATU pernyataan SELECT/WITH tanpa kata kunci pengubah data."""
    bersih = re.sub(r"--[^\n]*|/\*.*?\*/", " ", sql or "", flags=re.DOTALL).strip().rstrip(";").strip()
    if not bersih or ";" in bersih:
        return False
    if not re.match(r"^(select|with)\b", bersih, re.IGNORECASE):
        return False
    return not FORBIDDEN.search(bersih)


def _coba_koneksi():
    """Koneksi READ ONLY ke PostgreSQL; None jika tidak tersedia."""
    url = os.getenv("DATABASE_URL")
    if not url:
        _log("DATABASE_URL tidak ditemukan")
        return None
    try:
        conn = psycopg2.connect(url, cursor_factory=RealDictCursor, connect_timeout=5)
        conn.set_session(readonly=True)
        return conn
    except Exception as e:
        _log(f"Koneksi database gagal: {e}")
        return None


def get_db_connection():
    """Dipertahankan untuk kompatibilitas: koneksi PostgreSQL, atau berhenti dengan pesan ramah."""
    conn = _coba_koneksi()
    if conn is None:
        st.error("Database sementara tidak tersedia. Silakan coba beberapa saat lagi.")
        st.stop()
    return conn


def snapshot_tersedia():
    return SNAPSHOT_DIR.exists() and any(SNAPSHOT_DIR.glob("*.parquet"))


def _duckdb():
    """Koneksi DuckDB di memori dengan satu VIEW per file Parquet (nama tabel = nama file)."""
    import duckdb
    con = duckdb.connect()
    for f in sorted(SNAPSHOT_DIR.glob("*.parquet")):
        con.execute(f"CREATE VIEW \"{f.stem}\" AS SELECT * FROM read_parquet('{f.as_posix()}')")
    return con


def mode_data():
    """'live' (Supabase), 'snapshot' (cadangan Parquet), atau 'none'."""
    conn = _coba_koneksi()
    if conn is not None:
        conn.close()
        return "live"
    return "snapshot" if snapshot_tersedia() else "none"


@st.cache_data(ttl=3600, show_spinner=False)
def get_schema_info():
    """Informasi schema untuk konteks LLM: SEMUA tabel dasar (tanpa view), dari Supabase atau snapshot."""
    conn = _coba_koneksi()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT c.table_name, c.column_name, c.data_type
                    FROM information_schema.columns c
                    JOIN information_schema.tables t
                      ON t.table_name = c.table_name AND t.table_schema = c.table_schema
                    WHERE c.table_schema = 'public' AND t.table_type = 'BASE TABLE'
                    ORDER BY c.table_name, c.ordinal_position
                """)
                baris = [(r["table_name"], r["column_name"], r["data_type"]) for r in cur.fetchall()]
        finally:
            conn.close()
    elif snapshot_tersedia():
        con = _duckdb()
        baris = []
        for f in sorted(SNAPSHOT_DIR.glob("*.parquet")):
            for kolom, tipe, *_ in con.execute(f'DESCRIBE "{f.stem}"').fetchall():
                baris.append((f.stem, kolom, tipe.lower()))
        con.close()
    else:
        return ""

    tabel = {}
    for t, k, tipe in baris:
        tabel.setdefault(t, []).append(f"{k} ({tipe})")
    return "\n\n".join(f"Table: {t}\nColumns: {', '.join(cols)}" for t, cols in tabel.items())


def execute_query(sql_query):
    """Eksekusi SQL (hanya SELECT) dan kembalikan hasil dalam format yang sama seperti sebelumnya."""
    if not is_safe_select(sql_query):
        return {"success": False,
                "error": "Demi keamanan, asisten ini hanya menjalankan query SELECT (membaca data)."}

    conn = _coba_koneksi()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(sql_query)
                hasil = cur.fetchall() if cur.description else []
            conn.rollback()                      # sesi read-only: tidak ada yang perlu disimpan
            return {"success": True, "data": hasil, "row_count": len(hasil), "sumber": "live"}
        except Exception as e:
            return {"success": False, "error": str(e).split("\n")[0]}
        finally:
            conn.close()

    if snapshot_tersedia():
        try:
            con = _duckdb()
            df = con.execute(sql_query).fetchdf()
            con.close()
            df.columns = [("count" if c == "count_star()" else c) for c in df.columns]   # samakan nama dg PostgreSQL
            df = df.round(4)                                                         # rapikan sisa pembulatan float
            hasil = df.to_dict("records")
            return {"success": True, "data": hasil, "row_count": len(hasil), "sumber": "snapshot"}
        except Exception as e:
            _log(f"Query gagal di snapshot: {e}")
            return {"success": False, "error": str(e).split("\n")[0]}

    return {"success": False, "error": "Database sementara tidak tersedia. Silakan coba beberapa saat lagi."}
