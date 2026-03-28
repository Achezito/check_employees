import os
from supabase import create_client
from dotenv import load_dotenv
import streamlit as st

# Busca el .env relativo a este mismo archivo
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("❌ Faltan las variables SUPABASE_URL o SUPABASE_KEY en el archivo .env")

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)