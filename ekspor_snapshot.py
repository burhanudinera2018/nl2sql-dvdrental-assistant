"""
ekspor_snapshot.py — salin semua tabel dvdrental dari Supabase ke data_snapshot/*.parquet

Pemakaian (di laptop, sekali saja atau setiap data berubah):
    export DATABASE_URL="postgresql://...supabase.com:5432/postgres"   # jangan di-commit
    python ekspor_snapshot.py
    unset DATABASE_URL
"""
import decimal
import os
import sys
from pathlib import Path

import duckdb
import pandas as pd
import psycopg2

TUJUAN = Path(__file__).resolve().parent / "data_snapshot"


def rapikan(nilai):
    """Ubah tipe khusus PostgreSQL ke tipe yang aman untuk Parquet."""
    if isinstance(nilai, decimal.Decimal):
        return float(nilai)
    if isinstance(nilai, list):
        return "{" + ",".join(map(str, nilai)) + "}"
    if isinstance(nilai, (memoryview, bytes)):
        return None                                  # mis. foto staff: tidak diperlukan untuk demo
    return nilai


def main():
    url = os.getenv("DATABASE_URL")
    if not url:
        sys.exit("❌ Set DATABASE_URL dulu (lihat petunjuk di atas file ini).")
    TUJUAN.mkdir(exist_ok=True)
    pg = psycopg2.connect(url, connect_timeout=10)
    pg.set_session(readonly=True)
    cur = pg.cursor()
    cur.execute("""SELECT table_name FROM information_schema.tables
                   WHERE table_schema = 'public' AND table_type = 'BASE TABLE' ORDER BY table_name""")
    tabel = [r[0] for r in cur.fetchall()]
    dk = duckdb.connect()
    total = 0
    for t in tabel:
        cur.execute(f'SELECT * FROM "{t}"')
        kolom = [d[0] for d in cur.description]
        df = pd.DataFrame([[rapikan(v) for v in baris] for baris in cur.fetchall()], columns=kolom)
        for k in df.columns:                           # kolom yang seluruhnya kosong -> teks
            if df[k].isna().all():
                df[k] = df[k].astype("string")
        dk.register("sementara", df)
        dk.execute(f"COPY sementara TO '{(TUJUAN / (t + '.parquet')).as_posix()}' (FORMAT PARQUET)")
        dk.unregister("sementara")
        total += len(df)
        print(f"✅ {t:<15} {len(df):>6} baris")
    pg.close()
    ukuran = sum(f.stat().st_size for f in TUJUAN.glob("*.parquet")) / 1e6
    print(f"\nSelesai: {len(tabel)} tabel, {total} baris, {ukuran:.1f} MB di {TUJUAN.name}/")


if __name__ == "__main__":
    main()
