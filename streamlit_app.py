import streamlit as st
import openai
import numpy as np
from PIL import Image

# --- Page Setup ---
st.set_page_config(
    page_title="EC Classification Relativity Search Assistant",
    layout="centered"
)

# --- Load Logo ---
st.markdown("<style>img {display: block; margin-left: auto; margin-right: auto;}</style>", unsafe_allow_html=True)
icon = Image.open("4c2fb5e0-96aa-4846-a274-2e5021d1706b.png")
st.image(icon, width=150)

# --- App Title & Welcome Message ---
st.markdown("<h1 style='text-align: center;'>EC Classification Relativity Search Assistant</h1>", unsafe_allow_html=True)
st.write("""
<div style='text-align: center; font-size: 16px;'>
The classification relativity search assistant is designed to help users identify similar Government of Canada work descriptions using semantic and classification-level similarity in <strong>PCIS+</strong>.
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# --- API Key Setup ---
openai.api_key = st.secrets["OPENAI_API_KEY"]

# --- Session Setup ---
if "menu" not in st.session_state:
    st.session_state.menu = None

# --- Homepage Navigation ---
def show_home():
    st.markdown("### To start your relativity search, please select one of the menu options below:")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("
