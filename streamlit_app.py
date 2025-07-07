import streamlit as st
import openai
import numpy as np
from PIL import Image

# --- API Key Setup ---
openai.api_key = st.secrets["OPENAI_API_KEY"]

# --- Page Setup ---
st.set_page_config(
    page_title="EC Classification Relativity Search Assistant",
    layout="centered"
)

# --- Header with Icon and Title ---
col_icon, col_title = st.columns([1, 5])
with col_icon:
    st.image("4c2fb5e0-96aa-4846-a274-2e5021d1706b.png", width=80)
with col_title:
    st.markdown(
        "<h1 style='margin-bottom: 0;'>EC Classification Relativity Search Assistant</h1>",
        unsafe_allow_html=True
    )


# --- Home Page ---
def show_home():
    st.markdown("""
    <div style='font-size: 16px; padding-top: 0.5em;'>
        The Classification Relativity Search Assistant is designed to help users identify similar Government of Canada work descriptions in <strong>PCIS+</strong> using semantic similarity.<br><br>
        This app is powered by the OpenAI API, using a vector-based model called <strong>text-embedding-3-small</strong> to detect meaning-based similarity between work descriptions.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<div style='font-size:18px; font-weight:600; padding-top:10px;'>To start your relativity search, please select one of the menu options below:</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📤 Upload a Work Description", use_container_width=True):
            st.session_state.menu = "menu1"
            st.experimental_rerun()
        if st.button("📂 Search by Classification", use_container_width=True):
            st.session_state.menu = "menu3"
            st.experimental_rerun()

    with col2:
        if st.button("🔍 Search by Keywords", use_container_width=True):
            st.session_state.menu = "menu2"
            st.experimental_rerun()
        if st.button("📘 How Relativity Search Works", use_container_width=True):
            st.session_state.menu = "menu4"
            st.experimental_rerun()


# --- Menu 1 ---
def show_menu1():
    st.header("📎 Upload a Draft Work Description")

    st.markdown("""
    <div style='font-size: 16px;'>
    📎 <strong>You’ve selected: Upload a Work Description</strong><br><br>
    Please upload your draft job description in PDF or Word format or paste the text below.<br><br>
    Once uploaded or pasted, I’ll:<br>
    • Check if the role qualifies for EC classification using the official EC Standard<br>
    • If eligible, extract duties and responsibilities<br>
    • Compare it to existing EC jobs<br>
    • Return the top 3–5 most relevant comparators based on classification and functional similarity<br><br>
    I’ll then ask you to select one to view the full structured summary.
    </div>
    """, unsafe_allow_html=True)

    st.file_uploader("Upload a .docx or .txt file", type=["docx", "txt"])
    st.text_area("Or paste your job description here:")

    if st.button("🔙 Return to Main Menu – Menu 1"):
        st.session_state.menu = None
        st.experimental_rerun()


# --- Menu 2 ---
def show_menu2():
    st.header("🔍 Search by Keywords")
    st.info("Theme search feature coming soon.")
    if st.button("🔙 Return to Main Menu – Menu 2"):
        st.session_state.menu = None
        st.experimental_rerun()


# --- Menu 3 ---
def show_menu3():
    st.header("🧭 Search by Classification")
    st.info("Level browser feature coming soon.")
    if st.button("🔙 Return to Main Menu – Menu 3"):
        st.session_state.menu = None
        st.experimental_rerun()


# --- Menu 4 ---
def show_menu4():
    st.header("📘 How Relativity Search Works")

    with open("MENU_4_EXPLAINER.txt", "r") as f:
        explanation_text = f.read()
    st.markdown(explanation_text, unsafe_allow_html=True)

    if st.button("🔙 Return to Main Menu – Menu 4"):
        st.session_state.menu = None
        st.experimental_rerun()


# --- Routing Logic ---
menu = st.session_state.get("menu")

if menu == "menu1":
    show_menu1()
elif menu == "menu2":
    show_menu2()
elif menu == "menu3":
    show_menu3()
elif menu == "menu4":
    show_menu4()
else:
    show_home()
