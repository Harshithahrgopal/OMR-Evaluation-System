import os
import uuid
import sqlite3
import datetime
import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from PIL import Image
import numpy as np
import cv2

# --- PAGE CONFIG ---
st.set_page_config(page_title="Automated OMR Evaluation", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
        /* Main app background and default text color */
        .stApp {
            background-color: #f4f6f9;
            color: #1e3c72;  /* Dark blue text for readability */
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        /* Headers */
        h1, h2, h3 {
            color: #1e3c72;
            font-weight: 700;
        }

        /* Paragraphs, list items, spans */
        p, li, span {
            color: #1e3c72;
        }

        /* Streamlit Markdown text */
        .stMarkdown p, .stMarkdown li {
            color: #1e3c72;
        }

        /* Streamlit inputs and labels */
        label, .stText input, .stNumberInput input, .stSelectbox select {
            color: #1e3c72;
        }

        /* Placeholder text */
        .stText input::placeholder, .stNumberInput input::placeholder {
            color: #2a5298;  /* slightly darker blue for placeholders */
            opacity: 1;      /* ensures it’s visible */
        }

        /* Navbar / Option menu customization */
        .st-emotion-cache-1avcm0n { 
            background: linear-gradient(90deg, #1e3c72, #2a5298) !important; 
        }
        header[data-testid="stHeader"] { 
            background: linear-gradient(90deg, #2a5298, #1e3c72) !important; 
        }
        header[data-testid="stHeader"] * { color: white !important; }
        .nav-link { 
            font-size: 18px !important; 
            font-weight: 600 !important; 
            color: white !important; 
            margin-right: 20px; 
        }
        .nav-link:hover { 
            color: #ffcc00 !important; 
            transform: scale(1.05); 
        }

        /* Metric cards */
        .metric-card { 
            padding: 20px; 
            border-radius: 12px; 
            background: white; 
            box-shadow: 0 4px 12px rgba(0,0,0,0.08); 
            text-align: center; 
            height: 150px; 
            color: #1e3c72; 
        }

        /* Buttons and download buttons */
        .stButton>button, .stDownloadButton>button { 
            background: linear-gradient(90deg, #1e3c72, #2a5298); 
            color: white; 
            font-weight: 600; 
            border-radius: 8px; 
            padding: 8px 20px; 
            transition: all 0.3s ease; 
        }
        .stButton>button:hover, .stDownloadButton>button:hover { 
            background: linear-gradient(90deg, #2a5298, #1e3c72); 
            transform: scale(1.05); 
        }

        /* Footer */
        .footer { 
            position: fixed; 
            bottom: 0; 
            left: 0; 
            width: 100%; 
            background: #1e3c72; 
            color: white; 
            text-align: center; 
            padding: 10px; 
            font-size: 14px; 
            z-index: 999; 
        }

        /* Enhanced search bar styling */
        .st-emotion-cache-k3g7h5 p, .st-emotion-cache-k3g7h5 label { 
            font-size: 1.2rem; 
            font-weight: 600; 
            color: #1e3c72; 
        }
        .st-emotion-cache-k3g7h5 input[type="text"] {
            border: 2px solid #2a5298;
            border-radius: 8px;
            padding: 10px;
            font-size: 1rem;
            color: #1e3c72;
        }

        /* Table text (dataframes) */
        .stDataFrameWrapper td, .stDataFrameWrapper th {
            color: #1e3c72 !important;
        }

    </style>
""", unsafe_allow_html=True)


# --- DATABASE CONFIG ---
DB_PATH = "omr_results.db"
UPLOAD_DIR = "uploads"
KEY_DIR = os.path.join(UPLOAD_DIR, "keys")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(KEY_DIR, exist_ok=True)

def init_db():
    """Create results table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT,
        student_roll TEXT,
        class_batch TEXT,
        email TEXT,
        file_name TEXT,
        file_path TEXT,
        version TEXT,
        subject1 INTEGER DEFAULT 0,
        subject2 INTEGER DEFAULT 0,
        subject3 INTEGER DEFAULT 0,
        subject4 INTEGER DEFAULT 0,
        subject5 INTEGER DEFAULT 0,
        total_score INTEGER DEFAULT 0,
        flagged INTEGER DEFAULT 0,
        flag_reason TEXT,
        created_at TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS answer_keys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        version INTEGER,
        file_name TEXT,
        file_path TEXT,
        uploaded_at TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

def save_uploaded_file(uploaded_file, subdir=UPLOAD_DIR, prefix=None):
    """Save a Streamlit uploaded file to disk and return the saved path."""
    ext = os.path.splitext(uploaded_file.name)[1]
    unique = f"{prefix + '_' if prefix else ''}{uuid.uuid4().hex}{ext}"
    dest_folder = subdir
    os.makedirs(dest_folder, exist_ok=True)
    dest_path = os.path.join(dest_folder, unique)
    uploaded_file.seek(0)
    with open(dest_path, "wb") as f:
        f.write(uploaded_file.read())
    return dest_path, unique

def insert_result(row: dict):
    """Insert a result row into DB. `row` should contain keys matching columns."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO results
        (student_name, student_roll, class_batch, email, file_name, file_path, version,
         subject1, subject2, subject3, subject4, subject5, total_score, flagged, flag_reason, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        row.get("Student Name"),
        row.get("Student ID"),
        row.get("Class"),
        row.get("Email"),
        row.get("File Name"),
        row.get("File Path"),
        row.get("Version"),
        row.get("Subject 1", 0),
        row.get("Subject 2", 0),
        row.get("Subject 3", 0),
        row.get("Subject 4", 0),
        row.get("Subject 5", 0),
        row.get("Total Score", 0),
        row.get("Flagged", 0),
        row.get("Flag Reason"),
        row.get("Created At", datetime.datetime.now().isoformat())
    ))
    conn.commit()
    conn.close()

def fetch_all_results_df(limit=1000):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM results ORDER BY created_at DESC LIMIT ?", conn, params=(limit,))
    conn.close()
    return df

def load_answer_key(version: int):
    """
    Fetches the file path for a given answer key version.
    Returns the file path or None if not found.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT file_path FROM answer_keys WHERE version=? ORDER BY uploaded_at DESC LIMIT 1", (version,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    return None

def evaluate_omr(sheet_path, version):
    """
    Evaluates an OMR sheet against a saved answer key.
    
    NOTE: This function contains placeholder logic. You will need to implement
    the actual computer vision and data processing logic to make it fully functional.
    """
    key_path = load_answer_key(version)
    if not key_path:
        return {
            "Total Score": 0,
            "Flagged": 1,
            "Flag Reason": f"No answer key found for Version {version}",
        }

    answer_key = {}
    try:
        if key_path.lower().endswith(('.xlsx', '.xls', '.csv')):
            df_key = pd.read_csv(key_path, header=None)
            df_key = df_key.iloc[1:].reset_index(drop=True)
            for _, row in df_key.iterrows():
                for cell in row:
                    if pd.notna(cell) and ' - ' in str(cell):
                        parts = str(cell).split(' - ')
                        question = parts[0].strip()
                        answer = parts[1].strip()
                        if question.endswith('.'):
                            question = question[:-1]
                        if question.isdigit():
                            answer_key[int(question)] = answer
        else:
            answer_key = {i: "a" for i in range(1, 101)}

        if not answer_key:
            raise ValueError("Could not parse answer key data. Check format.")

    except Exception as e:
        return {
            "Total Score": 0,
            "Flagged": 1,
            "Flag Reason": f"Error parsing answer key: {e}",
        }

    try:
        # Replace this with your computer vision logic to detect filled bubbles
        student_answers = {
            1: 'a', 2: 'b', 3: 'c', 4: 'd', 5: 'c', 
            6: 'a', 7: 'c', 8: 'c', 9: 'b', 10: 'c'
        }
        
    except Exception as e:
        return {
            "Total Score": 0,
            "Flagged": 1,
            "Flag Reason": f"Evaluation failed: {e}",
        }

    correct_count = 0
    total_questions = len(answer_key)
    
    for question, correct_answer in answer_key.items():
        if student_answers.get(question) == correct_answer:
            correct_count += 1
            
    total_score = correct_count
    
    flagged = 0
    flag_reason = None
    if total_questions > 0 and len(student_answers) < total_questions:
        flagged = 1
        flag_reason = "Incomplete sheet detected."

    return {
        "Total Score": total_score,
        "Flagged": flagged,
        "Flag Reason": flag_reason,
        "Subject 1": total_score,
    }

# --- NAVBAR ---
selected = option_menu(
    menu_title=None,
    options=["Home", "Upload Sheets", "Results", "Flagged Sheets", "Admin Panel"],
    icons=["house", "cloud-upload", "table", "exclamation-triangle", "gear"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
)

# --- HOME PAGE ---
if selected == "Home":
    st.title("📊 Automated OMR Evaluation System")
    st.image("https://cdn-icons-png.flaticon.com/512/190/190411.png", width=120)
    st.markdown("""
        Welcome to the **Automated OMR Evaluation System** 🚀
        Upload OMR sheets, evaluate automatically, and view results instantly.
    """)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM results")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM results WHERE flagged=0")
    processed = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM results WHERE flagged=1")
    flagged = cursor.fetchone()[0]
    conn.close()

    st.subheader("Dashboard Overview")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="metric-card"><h3>📑 Sheets Uploaded</h3><h2>{total}</h2></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><h3>✅ Sheets Processed</h3><h2>{processed}</h2></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><h3>⏳ Pending Review</h3><h2>{flagged}</h2></div>', unsafe_allow_html=True)

# --- UPLOAD SHEETS PAGE ---
elif selected == "Upload Sheets":
    st.subheader("📝 Student Details")
    col1, col2 = st.columns(2)
    with col1:
        student_name = st.text_input("Student Name", placeholder="Enter full name")
    with col2:
        student_id = st.text_input("Student ID / Roll Number", placeholder="Enter roll number")
    
    col3, col4 = st.columns(2)
    with col3:
        student_class = st.text_input("Class / Batch", placeholder="e.g. 10th A / BSc CS")
    with col4:
        student_email = st.text_input("Email (optional)", placeholder="Enter email (if any)")
    
    st.header("📁 Upload OMR Sheets")
    uploaded_files = st.file_uploader(
        "Upload OMR Sheets (PDF/PNG/JPG)", 
        type=["pdf", "png", "jpg"], 
        accept_multiple_files=True
    )

    conn = sqlite3.connect(DB_PATH)
    versions_df = pd.read_sql_query("SELECT DISTINCT version FROM answer_keys", conn)
    conn.close()
    
    version_options = [str(v) for v in versions_df['version'].tolist()] if not versions_df.empty else ["No key available"]
    version = st.selectbox("Select Sheet Version", version_options)
    
    if st.button("🚀 Start Evaluation"):
        if uploaded_files and student_name and student_id and version != "No key available":
            st.success(f"{len(uploaded_files)} sheets uploaded for evaluation (Version: {version})")
            progress = st.progress(0)
            total_files = len(uploaded_files)
            for idx, file in enumerate(uploaded_files):
                saved_path, saved_filename = save_uploaded_file(file, subdir=UPLOAD_DIR, prefix=student_id)
                
                scores = evaluate_omr(saved_path, int(version))
                
                row = {
                    "Student Name": student_name,
                    "Student ID": student_id,
                    "Class": student_class,
                    "Email": student_email,
                    "File Name": saved_filename,
                    "File Path": saved_path,
                    "Version": version,
                    "Subject 1": scores.get("Subject 1", 0),
                    "Subject 2": scores.get("Subject 2", 0),
                    "Subject 3": scores.get("Subject 3", 0),
                    "Subject 4": scores.get("Subject 4", 0),
                    "Subject 5": scores.get("Subject 5", 0),
                    "Total Score": scores.get("Total Score", 0),
                    "Flagged": scores.get("Flagged", 0),
                    "Flag Reason": scores.get("Flag Reason"),
                    "Created At": datetime.datetime.now().isoformat()
                }
                insert_result(row)
                st.success(f"✅ {file.name} saved & evaluated for {student_name} ({student_id})")
                progress.progress(int(((idx+1)/total_files) * 100))
        else:
            st.error("⚠️ Please fill student details, upload files, and select a valid answer key version.")

# --- RESULTS PAGE ---
elif selected == "Results":
    st.header("📊 Evaluation Results")
    results_df = fetch_all_results_df(limit=5000)
    
    if not results_df.empty:
        # Enhanced search bar
        search_query = st.text_input("🔍 Search by student name or roll number...", placeholder="Type here to filter results...")
        if search_query:
            results_df = results_df[results_df["student_name"].str.contains(search_query, case=False) |
                                    results_df["student_roll"].str.contains(search_query, case=False)]

        st.dataframe(results_df.drop(columns=["file_path"]), use_container_width=True)
        
        # Selectbox to show detailed results
        selector_options = results_df.apply(lambda r: f"{r['student_name']} | {r['student_roll']} | {r['version']} | {r['created_at']}", axis=1).tolist()
        if selector_options:
            selector = st.selectbox("Select a result for details", selector_options)
            sel_idx = selector_options.index(selector)
            selected_row = results_df.iloc[sel_idx]
        
            st.info(f"Showing OMR sheet for **{selected_row['student_name']} ({selected_row['student_roll']})**")
            
            try:
                if selected_row['file_path'].lower().endswith(('.png', '.jpg', '.jpeg')):
                    st.image(Image.open(selected_row['file_path']), caption=f"{selected_row['file_name']}", use_column_width=True)
                else:
                    st.warning("Preview not available (file may be PDF).")
            except Exception as e:
                st.error(f"Could not preview file: {e}")
            
            st.markdown("### Scores")
            st.markdown(f"""
                **Student Name**: {selected_row["student_name"]}
                **Student ID**: {selected_row["student_roll"]}
                **Version**: {selected_row["version"]}
            """)
            st.write({
                "Subject 1": int(selected_row["subject1"]),
                "Subject 2": int(selected_row["subject2"]),
                "Subject 3": int(selected_row["subject3"]),
                "Subject 4": int(selected_row["subject4"]),
                "Subject 5": int(selected_row["subject5"]),
                "Total Score": int(selected_row["total_score"])
            })
        
        st.download_button("⬇️ Download Results (CSV)", results_df.to_csv(index=False), file_name="results.csv")
    else:
        st.info("ℹ️ No results available yet.")

# --- FLAGGED SHEETS PAGE ---
elif selected == "Flagged Sheets":
    st.header("⚠️ Flagged / Ambiguous Sheets")
    conn = sqlite3.connect(DB_PATH)
    flagged_df = pd.read_sql_query("SELECT * FROM results WHERE flagged=1 ORDER BY created_at DESC", conn)
    conn.close()

    search_query = st.text_input("🔍 Search student", placeholder="Type a name to filter...")
    if search_query:
        flagged_df = flagged_df[flagged_df["student_name"].str.contains(search_query, case=False)]

    if not flagged_df.empty:
        st.dataframe(flagged_df, use_container_width=True)
        choice = st.selectbox("Select flagged student", flagged_df["student_name"].unique())
        row = flagged_df[flagged_df["student_name"] == choice].iloc[0]
        st.warning(f"Reviewing sheet for **{choice}** — Reason: {row['flag_reason']}")
        try:
            st.image(Image.open(row['file_path']), caption=f"{row['file_name']}", use_column_width=True)
        except:
            st.info("Preview not available.")
        st.download_button("⬇️ Download Flagged Sheets (CSV)", flagged_df.to_csv(index=False), file_name="flagged_sheets.csv")
    else:
        st.info("No flagged sheets to display.")

# --- ADMIN PANEL PAGE ---
elif selected == "Admin Panel":
    st.header("⚙️ Admin Panel")
    st.text_input("Admin Username", placeholder="Enter admin username")
    st.text_input("Admin Password", placeholder="Enter password", type="password")

    st.subheader("🔑 Upload Answer Key")
    key_version = st.number_input("Assign Version / Set Number to this Answer Key", min_value=1, value=1, step=1)
    key_file = st.file_uploader("Upload Key File (Excel or Image)", type=["xlsx", "xls", "png", "jpg", "jpeg", "csv"])
    
    # Save button logic
    if st.button("💾 Save Answer Key"):
        if key_file:
            saved_path, saved_filename = save_uploaded_file(key_file, subdir=KEY_DIR, prefix=f"key_v{key_version}")
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO answer_keys (version, file_name, file_path, uploaded_at)
                VALUES (?, ?, ?, ?)
            """, (key_version, saved_filename, saved_path, datetime.datetime.now().isoformat()))
            conn.commit()
            conn.close()
            st.success(f"✅ Answer key uploaded for **Version {key_version}** and is ready for use.")
            if saved_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                st.image(Image.open(saved_path), caption=f"Answer Key (Version {key_version})", use_column_width=True)
        else:
            st.error("⚠️ Please upload a key file before saving.")

# --- FOOTER ---
st.markdown("""
    <div class="footer">
        © 2025 Automated OMR Evaluation System | Designed by TourShield
    </div>
""", unsafe_allow_html=True)
