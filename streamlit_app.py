import streamlit as st
import openai
import numpy as np
from PIL import Image

# --- API Key Setup ---
openai.api_key = st.secrets["OPENAI_API_KEY"]

import openai
import time

ASSISTANT_ID = "asst_dglLBL8pS8DzmBtFAv4SOUv2"  # Your Assistant ID from OpenAI

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

    if col1.button("📤 Upload a Work Description", use_container_width=True):
        st.session_state.menu = "menu1"
        st.rerun()
        return

    if col2.button("🔍 Search by Keywords", use_container_width=True):
        st.session_state.menu = "menu2"
        st.rerun()
        return

    if col1.button("📂 Search by Classification", use_container_width=True):
        st.session_state.menu = "menu3"
        st.rerun()
        return

    if col2.button("📘 How Relativity Search Works", use_container_width=True):
        st.session_state.menu = "menu4"
        st.rerun()
        return

# --- Menu 1 ---
def show_menu1():
    st.header("📎 Upload a Draft Work Description")

    st.markdown("""
    <div style='font-size: 16px;'>
    Please upload your draft job description in PDF or Word format or paste the text below.<br>
    Once uploaded or pasted, I’ll:<br>
    • Check if the role qualifies for EC classification using the official EC Standard<br>
    • If eligible, extract duties and responsibilities<br>
    • Compare it to existing EC jobs<br>
    • Return the top 3–5 most relevant comparators based on classification and functional similarity<br><br>
    I’ll then ask you to select one to view the full structured summary.
    </div>
    """, unsafe_allow_html=True)

    # ✅ Capture input into variables
    uploaded_file = st.file_uploader("Upload a .docx or .txt file", type=["docx", "txt"])
    pasted_text = st.text_area("Or paste your job description here:")

    if st.button("▶️ Submit Work Description"):
        if uploaded_file:
            user_input = uploaded_file.read().decode("utf-8")
        elif pasted_text.strip():
            user_input = pasted_text
        else:
            st.warning("Please upload a file or paste job description text.")
            return

        with st.spinner("Analyzing your work description..."):
            result = run_menu1_assistant(user_input)
        st.markdown(result)

    if st.button("🔙 Return to Main Menu – Menu 1"):
        st.session_state.menu = None
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
