import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from PIL import Image
import numpy as np

# --- PAGE CONFIG ---
st.set_page_config(page_title="Automated OMR Evaluation", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
        /* Background */
        .stApp {
            background-color: #f4f6f9;
        }
        /* Navbar gradient */
        .st-emotion-cache-1avcm0n {
            background: linear-gradient(90deg, #1e3c72, #2a5298) !important;
        }
        /* Streamlit header (Deploy + 3 dots) */
        header[data-testid="stHeader"] {
            background: linear-gradient(90deg, #2a5298, #1e3c72) !important;
        }
        header[data-testid="stHeader"] * {
            color: white !important;
        }
        /* Navbar links */
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
        h1, h2, h3 {
            color: #1e3c72;
        }
        /* Card styling */
        .metric-card {
            padding: 20px;
            border-radius: 12px;
            background: white;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            text-align: center;
            height: 150px;
        }
        /* Buttons */
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
    </style>
""", unsafe_allow_html=True)

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
    
    st.subheader("Dashboard Overview")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-card"><h3>📑 Sheets Uploaded</h3><h2>150</h2></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card"><h3>✅ Sheets Processed</h3><h2>120</h2></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card"><h3>⏳ Pending Review</h3><h2>30</h2></div>', unsafe_allow_html=True)

# --- UPLOAD SHEETS PAGE ---
elif selected == "Upload Sheets":
    st.subheader("📝 Student Details")
    col1, col2 = st.columns(2)
    with col1:
        student_name = st.text_input("Student Name", placeholder="Enter full name")
        student_id = st.text_input("Student ID / Roll Number", placeholder="Enter roll number")
    with col2:
        student_class = st.text_input("Class / Batch", placeholder="e.g. 10th A / BSc CS")
        student_email = st.text_input("Email (optional)", placeholder="Enter email (if any)")
    
    st.header("📁 Upload OMR Sheets")
    uploaded_files = st.file_uploader(
        "Upload OMR Sheets (PDF/PNG/JPG)", 
        type=["pdf", "png", "jpg"], 
        accept_multiple_files=True
    )
    
    version = st.selectbox("Select Sheet Version", ["Version A", "Version B"])
    
    if st.button("🚀 Start Evaluation"):
        if uploaded_files and student_name and student_id:
            st.success(f"{len(uploaded_files)} sheets uploaded for evaluation (Version: {version})")
            
            if "results_data" not in st.session_state:
                st.session_state.results_data = []
            
            for file in uploaded_files:
                st.session_state.results_data.append({
                    "Student Name": student_name,
                    "Student ID": student_id,
                    "Class": student_class,
                    "Email": student_email,
                    "File Name": file.name,
                    "Version": version,
                    "Subject 1": 0,
                    "Subject 2": 0,
                    "Subject 3": 0,
                    "Subject 4": 0,
                    "Subject 5": 0,
                    "Total Score": 0
                })
                st.success(f"✅ {file.name} ready for {student_name} ({student_id})")
            
            progress = st.progress(0)
            for i in range(101):
                progress.progress(i)
        else:
            st.error("⚠️ Please fill student details and upload files.")

# --- RESULTS PAGE ---
elif selected == "Results":
    st.header("📊 Evaluation Results")
    
    if "results_data" in st.session_state and st.session_state.results_data:
        results_df = pd.DataFrame(st.session_state.results_data)
        st.dataframe(results_df, use_container_width=True)
        
        selected_student = st.selectbox("Select Student to view sheet", results_df["Student Name"])
        student_row = results_df[results_df["Student Name"] == selected_student].iloc[0]
        st.info(f"Showing OMR sheet for **{student_row['Student Name']} ({student_row['Student ID']})**")
        
        img = np.ones((300, 400, 3), dtype=np.uint8) * 255
        img_pil = Image.fromarray(img)
        st.image(img_pil, caption=f"{selected_student}'s OMR Sheet", use_column_width=True)
        
        st.download_button("⬇️ Download Results (CSV)", results_df.to_csv(index=False), file_name="results.csv")
    else:
        st.info("ℹ️ No results available yet.")

# --- FLAGGED SHEETS PAGE ---
elif selected == "Flagged Sheets":
    st.header("⚠️ Flagged / Ambiguous Sheets")
    
    flagged_data = {
        "Student Name": ["David", "Emma"],
        "Issue": ["Ambiguous mark in Subject 2", "Skewed sheet image"]
    }
    flagged_df = pd.DataFrame(flagged_data)
    
    # Search bar
    search_query = st.text_input("🔍 Search student", placeholder="Type a name to filter...")
    if search_query:
        flagged_df = flagged_df[flagged_df["Student Name"].str.contains(search_query, case=False)]
    
    st.dataframe(flagged_df, use_container_width=True)
    
    if not flagged_df.empty:
        selected_flagged = st.selectbox("Select flagged student", flagged_df["Student Name"])
        st.warning(f"Reviewing sheet for **{selected_flagged}**")
        img_flagged = np.ones((300, 400, 3), dtype=np.uint8) * 200
        st.image(Image.fromarray(img_flagged), caption=f"{selected_flagged}'s OMR Sheet (Flagged)", use_column_width=True)
    
    # Download flagged data
    st.download_button("⬇️ Download Flagged Sheets (CSV)", 
                       flagged_df.to_csv(index=False), 
                       file_name="flagged_sheets.csv")

# --- ADMIN PANEL PAGE ---
elif selected == "Admin Panel":
    st.header("⚙️ Admin Panel")
    
    st.text_input("Admin Username", placeholder="Enter admin username")
    st.text_input("Admin Password", placeholder="Enter password", type="password")
    
    st.subheader("🔑 Upload Answer Key")
    
    # 1️⃣ Version / Set number input
    key_version = st.number_input(
        "Assign Version / Set Number to this Answer Key", 
        min_value=1, value=1, step=1,
        help="Assign a version number so OMR sheets can be validated against the correct key."
    )
    
    # 2️⃣ File uploader
    key_file = st.file_uploader("Upload Key File (Excel or Image)", type=["xlsx", "xls", "png", "jpg"])
    
    if key_file:
        if key_file.type in ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/vnd.ms-excel"]:
            df_key = pd.read_excel(key_file)
            if "answer_keys" not in st.session_state:
                st.session_state["answer_keys"] = {}
            st.session_state["answer_keys"][key_version] = df_key
          
            st.success(f"✅ Answer key uploaded (Excel) for Version {key_version}")
            st.dataframe(df_key, use_container_width=True)
        else:
            img_key = Image.open(key_file)
            if "answer_keys" not in st.session_state:
                st.session_state["answer_keys"] = {}
            st.session_state["answer_keys"][key_version] = img_key
            st.success(f"✅ Answer key uploaded (Image) for Version {key_version}")
            st.image(img_key, caption=f"Answer Key (Version {key_version})", use_column_width=True)

# --- FOOTER ---
st.markdown("""
    <div class="footer">
        © 2025 Automated OMR Evaluation System | Designed for Institutions
    </div>
""", unsafe_allow_html=True)
