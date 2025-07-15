import streamlit as st
import openai
from PIL import Image
import time
from docx import Document  # ✅ Add this line here
import pickle
import requests
import json                # Likely already present; skip if so
import numpy as np         # Needed for cosine similarity
from numpy.linalg import norm  # Needed for cosine similarity
import streamlit as st

import gdown
import gzip

@st.cache_data(show_spinner="📥 Downloading EC embeddings from Google Drive...")
def load_embeddings_from_drive():
    file_id = "1FW9Wn7Kchjb8LXY8JGZJmqPUx4cIqK8z"
    url = f"https://drive.google.com/uc?id={file_id}"

    output_path = "ec_embeddings.pkl.gz"
    gdown.download(url, output_path, quiet=False)

    with gzip.open(output_path, "rb") as f:
        return pickle.load(f)
# ✅ Load it once for use in your app
embedded_data = load_embeddings_from_drive()


# --- API Key Setup ---
openai.api_key = st.secrets["OPENAI_API_KEY"]
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
ASSISTANT_ID = "asst_dglLBL8pS8DzmBtFAv4SOUv2"  # Your Assistant ID from OpenAI
def cosine_similarity(vec1, vec2):
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    return float(np.dot(vec1, vec2) / (norm(vec1) * norm(vec2)))

element_weights = {
    "Decision Making": 0.21,
    "Leadership and Operational Management": 0.14,
    "Communication": 0.18,
    "Knowledge of Specialized Fields": 0.105,
    "Contextual Knowledge": 0.105,
    "Research and Analysis": 0.21,
    "Physical Effort": 0.015,
    "Sensory Effort": 0.01,
    "Working Conditions": 0.025
}

def interpret_match_quality(score):
    if score >= 0.90: return "Very Strong Match"
    elif score >= 0.85: return "Strong Match"
    elif score >= 0.80: return "OK Match"
    elif score >= 0.70: return "Weak Match"
    else: return "Very Weak Match"

def summarize_alignment(sim_scores):
    aligned = [k for k, v in sim_scores.items() if v >= 0.5]
    missing = [k for k, v in sim_scores.items() if v < 0.2]
    return f"Aligned: {', '.join(aligned)}. Missing: {', '.join(missing)}."

def run_comparator(user_elements, embedded_data, client):
    user_embeddings = {}
    for element, text in user_elements.items():
        if text.strip():
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text.strip()
            )
            user_embeddings[element] = response.data[0].embedding
        else:
            user_embeddings[element] = [0.0] * 1536

    results = []
    for record in embedded_data:
        sim_scores = {}
        total_score = 0.0

        for element, weight in element_weights.items():
            sim = cosine_similarity(user_embeddings[element], record["embeddings"].get(element, [0.0]*1536))
            sim_scores[element] = sim
            total_score += weight * sim

        level_penalty = 0.0  # TODO: add EC level logic later
        subject_penalty = 0.0  # TODO: add subject logic later
        final_score = total_score - level_penalty - subject_penalty

        results.append({
            "Job Title": record["Job Title"],
            "EC Level": record["EC Level"],
            "Department": record["Department"],
            "Final Score": round(final_score, 4),
            "Match Quality": interpret_match_quality(final_score),
            "Why it’s a Match": summarize_alignment(sim_scores)
        })

    return sorted(results, key=lambda x: x["Final Score"], reverse=True)[:5]



def run_menu1_assistant(user_input_text):
    # Step 1: Create a new thread
    thread = openai.beta.threads.create()

    # Step 2: Add user input to the thread
    openai.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_input_text
    )

    # Step 3: Run the assistant
    run = openai.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=ASSISTANT_ID
    )

    # Step 4: Wait for run to complete
    while True:
        run_status = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        if run_status.status == "completed":
            break
        elif run_status.status == "failed":
            return "⚠️ Assistant run failed."
        time.sleep(1)

    # Step 5: Get assistant message
    messages = openai.beta.threads.messages.list(thread_id=thread.id)
    for message in messages.data:
        if message.role == "assistant":
            return message.content[0].text.value

    return "⚠️ No assistant response found."

import re  # ✅ Make sure this is imported at the top

def extract_ec_elements(text, assistant_id, client):
    thread = client.beta.threads.create()
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=(
            "Please extract the following 9 EC classification elements from this job description:\n"
            "- Decision Making\n"
            "- Research and Analysis\n"
            "- Communication\n"
            "- Leadership and Operational Management\n"
            "- Knowledge of Specialized Fields\n"
            "- Contextual Knowledge\n"
            "- Physical Effort\n"
            "- Sensory Effort\n"
            "- Working Conditions\n\n"
            "Respond in JSON format with keys matching the EC elements.\n\n"
            f"Job description:\n{text}"
        )
    )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant_id
    )

    messages = client.beta.threads.messages.list(thread_id=thread.id)
    response_text = messages.data[0].content[0].text.value

    # ✅ Strip triple backticks and clean the JSON
    clean_text = re.sub(r"```(?:json)?\s*([\s\S]*?)\s*```", r"\1", response_text).strip()

    try:
        return json.loads(clean_text)
    except json.JSONDecodeError:
        st.warning("⚠️ Could not parse EC elements. Assistant response:")
        st.text_area("Raw Assistant Output", response_text, height=300)
        return None

# --- Page Setup ---
st.set_page_config(
    page_title="EC Classification Relativity Search Assistant",
    layout="centered"
)

# --- Header with Icon and Title ---
# --- Header with Icon and Title ---
col_icon, col_title = st.columns([1, 6])

with col_icon:
    st.markdown(
        "<div style='padding-top: 18px;'>",
        unsafe_allow_html=True
    )
    st.image("4c2fb5e0-96aa-4846-a274-2e5021d1706b.png", width=120)
    st.markdown("</div>", unsafe_allow_html=True)

with col_title:
    st.markdown(
        "<h1 style='margin-bottom: 0;margin-top: -12px;'>EC Classification Relativity Search Assistant</h1>",
        unsafe_allow_html=True
    )


# --- Home Page ---
def show_menu1():
    st.warning("🧪 You are seeing the NEW `show_menu1()`")

    if "view" not in st.session_state:
        st.session_state.view = "upload"
    if "results_displayed" not in st.session_state:
        st.session_state.results_displayed = 5
    if "last_results" not in st.session_state:
        st.session_state.last_results = []

    # ---------- PAGE: UPLOAD ----------
    if st.session_state.view == "upload":
        st.header("📎 Upload a Draft Work Description")
        st.markdown("""
        <div style='font-size: 16px;'>
        Please upload your draft job description in Word or paste the text below.<br><br>
        I will:<br>
        • Verify EC classification eligibility<br>
        • Extract duties & EC elements<br>
        • Compare it to EC dataset<br>
        • Return the top comparator matches
        </div>
        """, unsafe_allow_html=True)

        uploaded_file = st.file_uploader("Upload a .docx or .txt file", type=["docx", "txt"])
        pasted_text = st.text_area("Or paste your job description here:")

        if st.button("▶️ Submit Work Description"):
            if uploaded_file is not None:
                file_name = uploaded_file.name
                try:
                    if file_name.endswith(".docx"):
                        doc = Document(uploaded_file)
                        user_input = "\n".join([para.text for para in doc.paragraphs])
                    else:
                        user_input = uploaded_file.read().decode("utf-8")
                except Exception:
                    st.error("❌ Could not read uploaded file.")
                    return
            elif pasted_text.strip():
                user_input = pasted_text
            else:
                st.warning("Please upload a file or paste job description text.")
                return

            with st.spinner("Contacting EC Assistant..."):
                st.write("📝 Submitted input (preview):", user_input[:1000])
                user_elements = extract_ec_elements(user_input, ASSISTANT_ID, client)

            if user_elements:
                st.success("✅ EC Elements Extracted")
                st.json(user_elements)

                with st.spinner("Calculating best EC matches..."):
                    results = run_comparator(user_elements, embedded_data, client)
                    results = sorted(results, key=lambda x: x["Final Score"], reverse=True)

                    for i, r in enumerate(results):
                        r["#"] = i + 1
                        r["Link"] = f"[{r['Job Title']}](?job_id={i})"

                    st.session_state.last_results = results
                    st.session_state.view = "results"
                    st.session_state.results_displayed = 5
                    st.rerun()
            else:
                st.error("❌ Failed to extract EC elements. Please check input or assistant.")

    # ---------- PAGE: RESULTS ----------
    elif st.session_state.view == "results":
        all_results = st.session_state.last_results
        display_limit = min(st.session_state.results_displayed, 25)
        display_results = all_results[:display_limit]

        st.markdown("### 📊 Top Comparator Matches")

        # Markdown table only
        table_md = "| # | Job Title | EC Level | Department | Score | Match | Why it’s a Match |\n"
        table_md += "|---|------------|----------|------------|--------|--------|------------------|\n"
        for r in display_results:
            table_md += f"| {r['#']} | {r['Link']} | {r['EC Level']} | {r['Department']} | {r['Final Score']} | {r['Match Quality']} | {r['Why it’s a Match']} |\n"
        st.markdown(table_md)

        # Interpretation
        top_score = all_results[0]['Final Score']
        strong_matches = [r for r in all_results if r["Final Score"] >= 0.85]
        if top_score >= 0.85:
            interp = f"✅ {len(strong_matches)} comparators scored ≥ 0.85. These are strong matches."
        elif top_score >= 0.80:
            interp = "⚠️ Top matches are in the advisory range (0.80–0.84). Use with caution."
        else:
            interp = "⚠️ No comparators above 0.80. These are advisory only."
        st.markdown(f"**🔎 Interpretation:** {interp}")

        # Navigation Buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if display_limit < 25:
                if st.button("🔁 Show More Matches"):
                    st.session_state.results_displayed += 5
                    st.rerun()
        with col2:
            if st.button("🔄 Conduct Another Search"):
                st.session_state.view = "upload"
                st.session_state.results_displayed = 5
                st.session_state.last_results = []
                st.rerun()
        with col3:
            if st.button("🔙 Return to Main Menu"):
                st.session_state.menu = None
                st.session_state.view = "upload"
                st.session_state.results_displayed = 5
                st.session_state.last_results = []
                st.rerun()


# --- Menu 2 ---
def show_menu2():
    st.header("🔍 Search by Keywords")

    st.markdown("""
    <div style='font-size: 16px;'>
    🔍 <strong>You’ve selected: Search by Keywords</strong><br><br>
    Please describe the main duties, focus areas, or responsibilities of the draft job.<br><br>
    For example:<br>
    <em>“Policy research, stakeholder engagement, and performance reporting at EC-05.”</em><br><br>
    I’ll identify the key themes, compare them across our EC dataset, and return the most relevant work descriptions, ranked by semantic similarity.
    </div>
    """, unsafe_allow_html=True)

    user_keywords = st.text_input("Enter keywords or themes (e.g., policy, research, engagement):")

    if st.button("▶️ Search by Keywords"):
        st.info("Search results will appear here — functionality coming soon.")
   
    if st.button("🔙 Return to Main Menu – Menu 2"):
        st.session_state.menu = None
        st.rerun()
        return



# --- Menu 3 ---
def show_menu3():
    st.header("🧭 Search by Classification")

    st.markdown("""
    <div style='font-size: 16px;'>
    🧭 <strong>You’ve selected: Search by Classification</strong><br><br>
    
    Instead of listing random jobs, I’ll return top-scoring exemplars at that level — ranked by how closely each job aligns to the EC Classification Standard for that level.<br><br>
    For each match, you’ll see:<br>
    • A <strong>Level Fit Score</strong> (0–1.00), simulating how closely the job aligns with EC expectations at that level<br>
    • <strong>Key strengths</strong> (e.g., strong Research and Analysis, contextual complexity)<br>
    • <strong>Notes</strong> on why it's a standout match or edge case<br><br>
    This gives you a benchmarking view of what strong EC jobs look like at each level — helpful for relativity discussions, draft development, or classification advice.
    <br>    
    </div>
    """, unsafe_allow_html=True)

    selected_level = st.selectbox("Select EC Level", ["EC-01", "EC-02", "EC-03", "EC-04", "EC-05", "EC-06", "EC-07"])

    if st.button("▶️ View Jobs at This Level"):
        st.info(f"Results for {selected_level} will be shown here — feature coming soon.")

    if st.button("🔙 Return to Main Menu – Menu 3"):
        st.session_state.menu = None
        st.rerun()
        return


# --- Menu 4 ---
def show_menu4():
    st.header("📘 How Relativity Search Works")

    with open("MENU_4_EXPLAINER.txt", "r") as f:
        explanation_text = f.read()
    st.markdown(explanation_text, unsafe_allow_html=True)

    if st.button("🔙 Return to Main Menu – Menu 4"):
        st.session_state.menu = None
        st.rerun()
        return
# --- Home Page ---
def show_home():
    st.header("🏠 EC Classification Relativity Search Assistant")

    st.markdown("""
    <div style='font-size: 16px; line-height: 1.6;'>

    The <strong>EC Classification Relativity Search Assistant</strong> is designed to help Government of Canada classification advisors find high-quality comparator work descriptions within the <strong>Economics and Social Science Services (EC)</strong> group.
    <br>
    This prototype uses <strong>semantic similarity</strong> and <strong>classification-aligned evaluation logic</strong> to compare new or draft work descriptions against an internal EC dataset. Each record is evaluated using the nine official EC classification elements (e.g., Decision Making, Research and Analysis, Communication) and scored for alignment.
    <br>
    ⚙️ <strong>Powered by:</strong><br>
    • <strong>OpenAI GPT-4 API</strong> – for natural language understanding and EC element extraction<br>
    • <strong>OpenAI Embeddings (text-embedding-3-small)</strong> – for deep semantic comparison across job descriptions<br>
    • <strong>Weighted EC element scoring</strong> – using official EC evaluation weights to simulate classification reasoning<br><br>
    🧠 Unlike keyword search, this tool compares jobs based on meaning, complexity, and classification fit — helping advisors save time, improve consistency, and make better-informed level recommendations.
    <br>
    <strong>To begin your relativity search, select one of the menu options below:</strong>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("📎 Upload a Work Description"):
            st.session_state.menu = "menu1"
            st.rerun()
    with col2:
        if st.button("🔤 Search by Keywords"):
            st.session_state.menu = "menu2"
            st.rerun()
    with col3:
        if st.button("🧭 Search by Classification"):
            st.session_state.menu = "menu3"
            st.rerun()
    with col4:
        if st.button("📘 How Relativity Search Works"):
            st.session_state.menu = "menu4"
            st.rerun()

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
