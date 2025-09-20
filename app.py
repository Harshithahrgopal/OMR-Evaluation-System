import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from PIL import Image
import numpy as np

# --- PAGE CONFIG ---
st.set_page_config(page_title="Automated OMR Evaluation", layout="wide")

# --- NAVBAR ---
selected = option_menu(
    menu_title=None,
    options=["Home", "Upload Sheets", "Results", "Flagged Sheets"],
    icons=["house", "cloud-upload", "table", "exclamation-triangle"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
)

# --- HOME PAGE ---
if selected == "Home":
    st.title("📊 Automated OMR Evaluation System")
    st.image("https://cdn-icons-png.flaticon.com/512/190/190411.png", width=120)
    st.markdown("""
        Welcome to the **Automated OMR Evaluation System**.  
        Use the **Upload Sheets** tab to upload and evaluate OMR sheets.  
        View scores under **Results** and review ambiguous sheets under **Flagged Sheets**.
    """)
    
    # Dashboard Metrics (dummy numbers)
    st.subheader("Dashboard Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("Sheets Uploaded", 150)
    col2.metric("Sheets Processed", 120)
    col3.metric("Sheets Pending Review", 30)

# --- UPLOAD SHEETS PAGE ---
elif selected == "Upload Sheets":
    st.header("📁 Upload OMR Sheets")
    
    st.subheader("Enter Student Details")
    # --- STUDENT DETAILS FORM ---
    student_name = st.text_input("Student Name")
    student_id = st.text_input("Student ID / Roll Number")
    student_class = st.text_input("Class / Batch")
    student_email = st.text_input("Email (optional)")
    
    uploaded_files = st.file_uploader(
        "Upload OMR Sheets (PDF/PNG/JPG)", 
        type=["pdf", "png", "jpg"], 
        accept_multiple_files=True
    )
    
    version = st.selectbox("Select Sheet Version", ["Version A", "Version B"])
    
    if st.button("Start Evaluation"):
        if uploaded_files and student_name and student_id:
            st.success(f"{len(uploaded_files)} sheets uploaded for evaluation (Version: {version})")
            
            # Initialize session state list
            if "results_data" not in st.session_state:
                st.session_state.results_data = []
            
            # Store student details for each uploaded file
            for file in uploaded_files:
                st.session_state.results_data.append({
                    "Student Name": student_name,
                    "Student ID": student_id,
                    "Class": student_class,
                    "Email": student_email,
                    "File Name": file.name,
                    "Subject 1": 0,  # Placeholder marks
                    "Subject 2": 0,
                    "Subject 3": 0,
                    "Subject 4": 0,
                    "Subject 5": 0,
                    "Total Score": 0
                })
                st.write(f"✅ {file.name} ready for processing for {student_name} ({student_id})")
            
            # Simulate progress
            progress = st.progress(0)
            for i in range(101):
                progress.progress(i)
        else:
            st.error("Please fill all student details and upload at least one file.")

# --- RESULTS PAGE ---
elif selected == "Results":
    st.header("📊 Evaluation Results")
    
    if "results_data" in st.session_state and st.session_state.results_data:
        results_df = pd.DataFrame(st.session_state.results_data)
        st.dataframe(results_df)
        
        # Select student to view dummy OMR sheet
        selected_student = st.selectbox("Select Student to view sheet", results_df["Student Name"])
        student_row = results_df[results_df["Student Name"] == selected_student].iloc[0]
        st.write(f"Showing OMR sheet for **{student_row['Student Name']} ({student_row['Student ID']})**")
        
        # Dummy OMR image placeholder
        img = np.ones((300, 400, 3), dtype=np.uint8) * 255  # White blank image
        img_pil = Image.fromarray(img)
        st.image(img_pil, caption=f"{selected_student}'s OMR Sheet", use_column_width=True)
        
        # CSV download
        st.download_button("⬇️ Download CSV", results_df.to_csv(index=False), file_name="results.csv")
    else:
        st.info("No evaluation results to display yet.")

# --- FLAGGED SHEETS PAGE ---
elif selected == "Flagged Sheets":
    st.header("⚠️ Flagged / Ambiguous Sheets")
    
    # Dummy flagged sheets list
    flagged_data = {
        "Student Name": ["David", "Emma"],
        "Issue": ["Ambiguous mark in Subject 2", "Skewed sheet image"]
    }
    flagged_df = pd.DataFrame(flagged_data)
    
    st.dataframe(flagged_df)
    
    # Show placeholder sheet image for flagged student
    selected_flagged = st.selectbox("Select flagged student", flagged_df["Student Name"])
    st.write(f"Reviewing sheet for **{selected_flagged}**")
    img_flagged = np.ones((300, 400, 3), dtype=np.uint8) * 200  # Gray placeholder
    st.image(Image.fromarray(img_flagged), caption=f"{selected_flagged}'s OMR Sheet (Flagged)", use_column_width=True)
