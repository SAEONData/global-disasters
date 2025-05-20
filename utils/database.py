import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
import pandas as pd
import streamlit as st

load_dotenv()

DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")
DB_NAME = os.getenv("POSTGRES_DB")

# SQLAlchemy engine
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

@st.cache_data(ttl=600)
def get_full_data():
    query = "SELECT * FROM public.emdata_hist"
    return pd.read_sql_query(query, engine)

def get_filtered_data(filters: dict):
    """Optional later: SQL-based dynamic filtering."""
    where_clauses = []
    if filters.get('country'):
        where_clauses.append(f"country = '{filters['country']}'")
    if filters.get('start_year'):
        where_clauses.append(f"start_date >= '{filters['start_year']}-01-01'")
    if filters.get('end_year'):
        where_clauses.append(f"end_date <= '{filters['end_year']}-12-31'")

    where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
    query = f"SELECT * FROM public.emdata_hist {where_clause}"
    return pd.read_sql_query(query, engine)
