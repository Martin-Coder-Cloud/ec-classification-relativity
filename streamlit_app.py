import streamlit as st
import openai
import numpy as np
from PIL import Image

# --- Page Setup ---
st.set_page_config(
    page_title="EC Classification Relativity Search Assistant",
    layout="centered"
)

# --- Load App Icon ---
st.markdown("<style>img {display: block; margin-left: auto; margin-right: auto;}</style>", unsafe_allow_html=True)
icon = Image.open("4c2fb5e0-96aa-4846-a274-2e5021d1706b.png")  # Your uploaded image filename
st.image(icon, width=150)

# --- Title & Welcome ---
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

# --- Navigation Menu ---
def show_home():
    st.subheader("Choose an option:")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📎 Upload Work Description", use_container_width=True):
            st.session_state.menu = "menu1"
    with col2:
        if st.button("🔍 Search by Theme", use_container_width=True):
            st.session_state.menu = "menu2"
    col3, col4 = st.columns(2)
    with col3:
        if st.button("📊 Browse by EC Level", use_container_width=True):
            st.session_state.menu = "menu3"
    with col4:
        if st.button("📘 Relativity Explainer", use_container_width=True):
            st.session_state.menu = "menu4"

# --- Menu 1: Upload & Compare ---
def show_menu1():
    st.header("📎 Upload a Work Description")
    uploaded_file = st.file_uploader("Upload a .docx or .txt file", type=["docx", "txt"])
    if uploaded_file:
        text = uploaded_file.read().decode("utf-8", errors="ignore")
        st.success("File uploaded successfully.")

        user_embedding = openai.embeddings.create(input=[text], model="text-embedding-3-small").data[0].embedding

        comparator_db = [
            {
                "job_title": "Policy Analyst",
                "ec_level": "EC-05",
                "department": "ESDC",
                "text": "Develops policies, performs analysis of government programs, and prepares briefing materials.",
                "view_id": "ec_record_001"
            },
            {
                "job_title": "Evaluation Officer",
                "ec_level": "EC-04",
                "department": "PSC",
                "text": "Conducts program evaluations, manages data collection, and supports reporting to senior officials.",
                "view_id": "ec_record_002"
            },
            {
                "job_title": "Stakeholder Engagement Advisor",
                "ec_level": "EC-06",
                "department": "IRCC",
                "text": "Facilitates consultations, synthesizes input for policy development, and liaises with external partners.",
                "view_id": "ec_record_003"
            }
        ]

        def cosine_similarity(a, b):
            a, b = np.array(a), np.array(b)
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

        def interpret_score(score):
            if score >= 0.9:
                return "Very Strong Match"
            elif score >= 0.85:
                return "Strong Match"
            elif score >= 0.8:
                return "OK Match"
            elif score >= 0.75:
                return "Weak Match"
            else:
                return "Very Weak Match"

        results = []
        for record in comparator_db:
            emb = openai.embeddings.create(input=[record["text"]], model="text-embedding-3-small").data[0].embedding
            score = cosine_similarity(user_embedding, emb)
            results.append({
                "job_title": record["job_title"],
                "ec_level": record["ec_level"],
                "department": record["department"],
                "score": round(score, 3),
                "match_quality": interpret_score(score),
                "view_id": record["view_id"]
            })

        results = sorted(results, key=lambda x: x["score"], reverse=True)

        st.subheader("Comparator Results")
        st.table(results)

        if st.button("🔙 Return to Main Menu"):
            st.session_state.menu = None

# --- Placeholder Menus ---
def show_menu2():
    st.header("🔍 Search by Theme")
    st.info("Theme search feature coming soon.")
    if st.button("🔙 Return to Main Menu"):
        st.session_state.menu = None

def show_menu3():
    st.header("📊 Browse by EC Level")
    st.info("Level browser feature coming soon.")
    if st.button("🔙 Return to Main Menu"):
        st.session_state.menu = None

def show_menu4():
    st.header("📘 Relativity Explainer")
    st.markdown("""
    - This tool compares uploaded work descriptions to a reference dataset.
    - Matches are based on alignment with EC classification elements.
    - Match quality is simulated using semantic embeddings.
    """)
    if st.button("🔙 Return to Main Menu"):
        st.session_state.menu = None

# --- Routing ---
if st.session_state.menu == "menu1":
    show_menu1()
elif st.session_state.menu == "menu2":
    show_menu2()
elif st.session_state.menu == "menu3":
    show_menu3()
elif st.session_state.menu == "menu4":
    show_menu4()
else:
    show_home()
