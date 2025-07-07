import streamlit as st
import openai
import json

# --- Configuration ---
st.set_page_config(page_title="EC Classification Relativity", layout="wide")
openai.api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else ""

# --- App Title ---
st.title("📘 EC Classification Relativity Assistant")

# --- Sidebar Menu ---
menu = st.sidebar.radio("Choose a menu option:", [
    "📎 Menu 1 – Upload a Work Description",
    "🔍 Menu 2 – Search by Theme",
    "📊 Menu 3 – Browse by EC Level",
    "📘 Menu 4 – Relativity Explainer"
])

# --- Sample Comparator DB (to be replaced with real dataset) ---
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

# --- Utilities ---
def get_embedding(text):
    response = openai.embeddings.create(
        input=[text],
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def cosine_similarity(a, b):
    import numpy as np
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

# --- Menu 1: Upload Work Description ---
if menu == "📎 Menu 1 – Upload a Work Description":
    uploaded_file = st.file_uploader("Upload a .docx or .txt file", type=["docx", "txt"])
    
    if uploaded_file:
        user_text = uploaded_file.read().decode("utf-8", errors="ignore")
        st.markdown("✅ **File uploaded successfully.** Now analyzing...")

        user_embedding = get_embedding(user_text)

        results = []
        for record in comparator_db:
            comp_emb = get_embedding(record["text"])
            score = cosine_similarity(user_embedding, comp_emb)
            match_quality = interpret_score(score)
            results.append({
                "rank": None,
                "job_title": record["job_title"],
                "ec_level": record["ec_level"],
                "department": record["department"],
                "score": round(score, 3),
                "match_quality": match_quality,
                "why_match": "Simulated match explanation (to be implemented)",
                "view_id": record["view_id"]
            })

        # Sort results
        results = sorted(results, key=lambda x: x["score"], reverse=True)
        for idx, r in enumerate(results):
            r["rank"] = idx + 1

        # Display
        st.subheader("📊 Comparator Results")
        st.table([{k: r[k] for k in ("rank", "job_title", "ec_level", "department", "score", "match_quality")} for r in results])

        st.subheader("🧠 Interpretation")
        top_result = results[0]
        st.markdown(f"- **Top match:** {top_result['job_title']} ({top_result['ec_level']}) – Score: {top_result['score']} → *{top_result['match_quality']}*")
        st.markdown("- All results are simulated. Actual EC element matching will be integrated in future versions.")

# --- Menu 2: Search by Theme ---
elif menu == "🔍 Menu 2 – Search by Theme":
    st.info("🔧 This menu will let you search using keywords or duty statements. Coming next.")

# --- Menu 3: Browse by EC Level ---
elif menu == "📊 Menu 3 – Browse by EC Level":
    st.info("🔧 This menu will benchmark your work vs. EC level descriptions. Coming soon.")

# --- Menu 4: Relativity Explainer ---
elif menu == "📘 Menu 4 – Relativity Explainer":
    st.markdown("""
    ### 🔍 What is a Comparator Match?
    - Comparator results simulate alignment with EC classification elements.
    - Matching is based on semantic similarity of duties, responsibilities, and context.
    - Scores above 0.85 are generally considered valid for advisory purposes.

    ### 🧠 Match Quality Thresholds
    - 0.90+ → Very Strong Match
    - 0.85–0.89 → Strong Match
    - 0.80–0.84 → OK Match
    - 0.75–0.79 → Weak Match
    - < 0.75 → Very Weak Match

    *Note: Actual EC compliance checks are advisory only.*
    """)

