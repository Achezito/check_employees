import streamlit as st

def apply_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500&display=swap');

    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

    .stApp { background-color: #0e0e0e; color: #e8e8e8; }

    section[data-testid="stSidebar"] {
        background-color: #141414;
        border-right: 1px solid #2a2a2a;
    }
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 { color: #e8e8e8 !important; }

    h1 { font-family: 'Space Mono', monospace !important; color: #ffffff !important; letter-spacing: -1px; }
    h2, h3 { font-family: 'Space Mono', monospace !important; color: #cccccc !important; }

    input, textarea, select {
        background-color: #1a1a1a !important;
        color: #e8e8e8 !important;
        border: 1px solid #333 !important;
        border-radius: 4px !important;
    }

    .stButton > button {
        background-color: #ffffff !important;
        color: #000000 !important;
        font-family: 'Space Mono', monospace !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 2px !important;
        padding: 0.5rem 1.5rem !important;
        letter-spacing: 1px !important;
        transition: all 0.2s !important;
    }
    .stButton > button:hover { background-color: #00ff99 !important; color: #000000 !important; }

    .stDataFrame { border: 1px solid #2a2a2a; border-radius: 4px; }

    [data-testid="metric-container"] {
        background-color: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 4px;
        padding: 1rem;
    }
    [data-testid="metric-container"] label { color: #888 !important; font-size: 0.75rem !important; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-family: 'Space Mono', monospace !important;
    }

    .stSuccess { background-color: #0d2b1f !important; border-left: 3px solid #00ff99 !important; color: #00ff99 !important; }
    .stError   { background-color: #2b0d0d !important; border-left: 3px solid #ff4444 !important; color: #ff4444 !important; }
    .stWarning { background-color: #2b240d !important; border-left: 3px solid #ffaa00 !important; color: #ffaa00 !important; }
    .stInfo    { background-color: #0d1e2b !important; border-left: 3px solid #4499ff !important; color: #4499ff !important; }

    hr { border-color: #2a2a2a !important; }

    .stTabs [data-baseweb="tab-list"] { background-color: #141414; border-bottom: 1px solid #2a2a2a; }
    .stTabs [data-baseweb="tab"] { color: #888 !important; font-family: 'Space Mono', monospace !important; font-size: 0.8rem !important; }
    .stTabs [aria-selected="true"] { color: #ffffff !important; border-bottom: 2px solid #00ff99 !important; }
    </style>
    """, unsafe_allow_html=True)
