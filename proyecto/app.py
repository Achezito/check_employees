import streamlit as st
from config import init_supabase
from styles import apply_styles
from modules import dashboard, empleados, huellas, asistencia, pagos

# ── Config ───────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sistema de Asistencia",
    page_icon="🖐️",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_styles()

supabase = init_supabase()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("# 🖐️ CHECADOR")
    st.markdown("---")
    opcion = st.selectbox("MÓDULO", [
        "📊 Dashboard",
    
        "👤 Empleados",
        "🖐️ Huellas",
        "🕐 Asistencia",
  
        "💰 Pagos",
    ])
    st.markdown("---")
    st.markdown("<small style='color:#444'>v1.0 · Supabase</small>", unsafe_allow_html=True)

# ── Routing ───────────────────────────────────────────────────────────────────
if   opcion == "📊 Dashboard":          dashboard.render(supabase)
elif opcion == "👤 Empleados":          empleados.render(supabase)
elif opcion == "🖐️ Huellas":           huellas.render(supabase)
elif opcion == "🕐 Asistencia":         asistencia.render(supabase)
elif opcion == "💰 Pagos":              pagos.render(supabase)