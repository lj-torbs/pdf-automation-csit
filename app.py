import os
import streamlit as st
import pandas as pd
from generators.logsheet import generate_logsheet_with_details
from generators.seatplan import generate_seatplan
from generators.syllabi import generate_syllabi
from PyPDF2 import PdfMerger
from datetime import datetime
from datetime import time
import base64
from pathlib import Path

st.set_page_config(
    page_title="Life Support PDF Generator",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_css():
    st.markdown("""
    <style>
        /* Main container styling - using UM Maroon */
        .main-header {
            background: linear-gradient(135deg, #7B2F26 0%, #A45D4A 100%);
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            color: white;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .main-header h1 {
            margin: 0;
            font-size: 2.5rem;
            font-weight: 600;
        }
        
        .main-header p {
            margin: 0.5rem 0 0 0;
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        /* Card styling */
        .card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;
            border: 1px solid #D4B48C; /* Coffee color border */
        }
        
        .card-header {
            border-bottom: 2px solid #7B2F26; /* UM Maroon */
            padding-bottom: 0.5rem;
            margin-bottom: 1rem;
            font-weight: 600;
            color: #4A2C1A; /* Dark coffee brown */
        }
        
        /* Metric cards - using coffee/beige tones */
        .metric-card {
            background: linear-gradient(135deg, #F5E6D3 0%, #E6D5B8 100%);
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: #7B2F26; /* UM Maroon */
        }
        
        .metric-label {
            font-size: 0.9rem;
            color: #6B4F3A; /* Coffee brown */
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        /* Button styling - using UM Maroon gradient */
        .stButton > button {
            background: linear-gradient(135deg, #7B2F26 0%, #A45D4A 100%);
            color: white;
            border: none;
            padding: 0.75rem 2rem;
            font-weight: 600;
            border-radius: 8px;
            transition: all 0.3s ease;
            width: 100%;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(123, 47, 38, 0.4); /* Maroon shadow */
        }
        
        /* Download buttons */
        .stDownloadButton > button {
            background: white;
            color: #7B2F26; /* UM Maroon */
            border: 2px solid #7B2F26;
            padding: 0.5rem 1rem;
            font-weight: 600;
            border-radius: 8px;
            transition: all 0.3s ease;
        }
        
        .stDownloadButton > button:hover {
            background: #7B2F26;
            color: white;
        }
        
        /* Expander styling - using coffee tones */
        .streamlit-expanderHeader {
            background: linear-gradient(135deg, #F5E6D3 0%, #E6D5B8 100%);
            border-radius: 8px;
            border: none;
            font-weight: 600;
            color: #4A2C1A; /* Dark coffee */
        }
        
        /* Progress bar - using maroon to coffee gradient */
        .stProgress > div > div {
            background: linear-gradient(90deg, #7B2F26 0%, #C49A6C 100%);
        }
        
        /* Success/Warning/Info messages */
        .stAlert {
            border-radius: 8px;
            border-left: 4px solid;
        }
        
        /* Success message */
        .stAlert.success {
            border-left-color: #7B2F26;
        }
        
        /* File uploader */
        .uploadedFile {
            background: #FDF8F0; /* Light cream */
            border: 2px dashed #7B2F26; /* Maroon */
            border-radius: 8px;
            padding: 1rem;
        }
        
        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
            background: #F5E6D3; /* Light coffee */
            padding: 0.5rem;
            border-radius: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 6px;
            padding: 0.5rem 1rem;
            font-weight: 600;
            color: #4A2C1A;
        }
        
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background: #7B2F26;
            color: white;
        }
        
        /* Sidebar */
        .css-1d391kg {
            background: linear-gradient(180deg, #FDF8F0 0%, #F5E6D3 100%);
        }
        
        /* Info boxes */
        .stInfo {
            background-color: #F5E6D3;
            color: #4A2C1A;
        }
        
        /* Success boxes */
        .stSuccess {
            background-color: #E6D5B8;
            color: #4A2C1A;
        }
        
        /* Footer */
        .footer {
            text-align: center;
            padding: 2rem;
            color: #6B4F3A; /* Coffee brown */
            font-size: 0.9rem;
            border-top: 2px solid #D4B48C; /* Light coffee */
            margin-top: 3rem;
        }
        
        /* Radio buttons and checkboxes */
        .stCheckbox {
            color: #4A2C1A;
        }
        
        .stCheckbox [data-baseweb="checkbox"]:checked {
            background-color: #7B2F26;
            border-color: #7B2F26;
        }
        
        /* Text inputs */
        .stTextInput input {
            border: 1px solid #D4B48C;
        }
        
        .stTextInput input:focus {
            border-color: #7B2F26;
            box-shadow: 0 0 0 1px #7B2F26;
        }
        
        /* Select boxes */
        .stSelectbox [data-baseweb="select"] {
            border-color: #D4B48C;
        }
        
        .stSelectbox [data-baseweb="select"]:focus {
            border-color: #7B2F26;
        }
    </style>
    """, unsafe_allow_html=True)

if 'generation_complete' not in st.session_state:
    st.session_state.generation_complete = False
if 'generated_files' not in st.session_state:
    st.session_state.generated_files = []

load_css()

st.markdown("""
<div class="main-header">
    <h1>Syllabus, Exam & Seatplan Generator (SES Generator)</h1>
    <p>Made for Don Benjamin</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("----->Quick Guide")
    st.info(
        """
        **How to use:**
        1. Upload Excel files with student names from MIS Example:(ClassList-2026-4541.xlsx)
        2. Select documents to generate
        3. Fill in class details and faculty information
        4. Click 'Generate PDF Documents'
        """
    )

    # Contact/Support
    st.markdown("---")
    st.markdown("### Need Help?")
    st.markdown("lorcullo@umindanao.edu.ph")
    st.markdown("+639664885750")

# Main content area
tab1, tab2, tab3 = st.tabs(["📁 Upload Files", "⚙️ Configuration", "📥 Downloads"])

with tab1:
    #st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("""
<style>
.card-header {
    font-size: 18px;
    font-weight: 600;
    color: var(--text-color);
}
</style>
""", unsafe_allow_html=True)

    st.markdown('<p class="card-header">Upload Class Lists</p>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "Drag and drop your Excel files here",
        type=['xlsx', 'xls'],
        accept_multiple_files=True,
        help="Upload one or more Excel files containing student names"
    )
    
    if uploaded_files:
        st.success(f"{len(uploaded_files)} file(s) uploaded successfully")
    st.markdown('</div>', unsafe_allow_html=True)

# Process uploaded files
if uploaded_files:
    all_data = []
    
    # Progress bar for file processing
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, uploaded_file in enumerate(uploaded_files):
        status_text.text(f"Processing {uploaded_file.name}...")
        
        try:
            df = pd.read_excel(
                uploaded_file,
                engine="openpyxl",
                dtype=str,
                header=None
            )
            
            df = df.fillna("")
            
            header_row = None
            for i, row in df.iterrows():
                row_values = [str(cell).lower() for cell in row.values]
                if any("name" in cell for cell in row_values):
                    header_row = i
                    break
            
            if header_row is not None:
                df.columns = df.iloc[header_row]
                df = df[header_row + 1:]
                df.columns = df.columns.str.strip().str.lower()
            else:
                st.error(f"{uploaded_file.name}: Could not detect header row")
                continue
            
            name_col = None
            possible_cols = ['std_name', 'name', 'student name', 'full name']
            
            for col in df.columns:
                if col in possible_cols:
                    name_col = col
                    break
            
            if name_col:
                students = df[name_col].tolist()
                students = [s for s in students if s]  # Remove empty names
                
                all_data.append({
                    "filename": uploaded_file.name,
                    "students": students
                })
            else:
                st.error(f"{uploaded_file.name} has no valid name column")
        
        except Exception as e:
            st.error(f"Error reading {uploaded_file.name}: {str(e)}")
        
        progress_bar.progress((idx + 1) / len(uploaded_files))
    
    status_text.text("File processing complete!")
    progress_bar.empty()
    
    if all_data:
        with tab1:
            # Display summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            total_classes = len(all_data)
            total_students = sum(len(data["students"]) for data in all_data)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{total_classes}</div>
                    <div class="metric-label">Classes Loaded</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{total_students}</div>
                    <div class="metric-label">Total Students</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                avg_per_class = total_students // total_classes if total_classes > 0 else 0
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{avg_per_class}</div>
                    <div class="metric-label">Avg per Class</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{len(uploaded_files)}</div>
                    <div class="metric-label">Files Uploaded</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Preview section
            st.markdown('<p class="card-header">👥 Class Lists Preview</p>', unsafe_allow_html=True)
            
            st.markdown("""
<style>
.fake-button {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 6px;
    background-color: var(--secondary-background-color);
    color: var(--text-color);
    font-weight: 500;
    font-size: 14px;
    margin-bottom: 10px;
    cursor: pointer;
    transition: all 0.2s ease;
}
.fake-button:hover {
    opacity: 0.85;
    transform: scale(1.03);
}
</style>
""", unsafe_allow_html=True)
            
            for data in all_data:
                with st.expander(f"Preview classlist for {data['filename']}"):
                

                    preview_df = pd.DataFrame({
                        "#": range(1, len(data["students"]) + 1),
                        "Student Name": data["students"]
                    })

                    st.dataframe(
                        preview_df,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "#": st.column_config.NumberColumn(format="%d"),
                            "Student Name": st.column_config.TextColumn(width="large")
                        }
                    )

            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab2:
            # Configuration section
            st.markdown('<p class="card-header">Document Selection</p>', unsafe_allow_html=True)
            
            
            col_a, col_b, col_c, col_d = st.columns(4)
            
            with col_a:
                select_all = st.checkbox("Select All Documents", value=False)            
            with col_b:
                gen_seatplan = st.checkbox("Seat Plan", value=select_all)
            
            with col_c:
                gen_syllabi = st.checkbox("Syllabi", value=select_all)
            with col_d:
                gen_logsheet = st.checkbox("Logsheet", value=select_all)

            st.markdown('</div>', unsafe_allow_html=True)
            
            # Header Information
            st.markdown('<p class="card-header">👤 Header Information</p>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                faculty_name = st.text_input(
                    "Faculty Name",
                    placeholder="e.g., Dr. John Smith",
                    help="Enter the full name of the faculty member"
                )
                
                program_head = st.text_input(
                    "Program Head",
                    placeholder="e.g., Prof. Jane Doe",
                    help="Enter the name of the program head"
                )

                branch = st.radio(
                    "Campus",
                    ["Main", "Branch"],
                    horizontal=True
                )

                subject_type = st.radio(
                    "Subject Type",
                    ["Term", "Semestral"],
                    horizontal=True,
                )
            
            with col2:
                col_sem, col_term, col_sy = st.columns(3)
                
                with col_sem:
                    semester = st.selectbox(
                        "Semester",
                        ["1st", "2nd", "Summer"],
                        index=0
                    )
                
                with col_term:
                    term = st.selectbox(
                        "Term",
                        ["1st", "2nd"],
                        index=0
                    )
                
                with col_sy:
                    current_year = datetime.now().year
                    current_month = datetime.now().month
                    
                    if current_month < 6:
                        start_year = current_year - 1
                    else:
                        start_year = current_year
                    
                    school_years = [
                        f"{start_year+i}-{start_year+i+1}"
                        for i in range(0, 5)
                    ]
                    
                    school_year = st.selectbox(
                        "School Year",
                        school_years,
                        index=0
                    )
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Per Class Settings
            st.markdown('<p class="card-header">⚙️ General Setup</p>', unsafe_allow_html=True)
            
            class_settings = []
            
            for i, data in enumerate(all_data):
                with st.expander(f"⚙️ Setup form for {data['filename']}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        subject_code = st.text_input(
                            "Subject",
                            key=f"sub_{i}",
                            placeholder="e.g., MATH101"
                        )
                    
                    with col2:
                        code_section = st.text_input(
                            "Code/Section",
                            key=f"sec_{i}",
                            placeholder="e.g., 4616"
                        )
                    
                    with col3:
                        col_start, col_end = st.columns(2)
                        
                        with col_start:
                            start_time = st.time_input(
                                "Start Time",
                                value=time(9, 0),
                                key=f"start_time_{i}"
                            )

                        with col_end:
                            end_time = st.time_input(
                                "End Time",
                                value=time(10, 30),
                                key=f"end_time_{i}"
                            )

                        time_range = f"{start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}"
                    
                    col4, col5, col6 = st.columns(3)
                    
                    with col4:
                        room = st.text_input(
                            "Room",
                            key=f"room_{i}",
                            placeholder="e.g., Room 201"
                        )
                    
                    with col5:
                        college = st.text_input(
                            "College",
                            key=f"col_{i}",
                            placeholder="e.g., College of Science"
                        )
                    
                    with col6:
                        program = st.text_input(
                            "Program",
                            key=f"prog_{i}",
                            placeholder="e.g., BS Computer Science"
                        )
                    
                    if subject_code and code_section:
                        st.info(f"**Summary:** {subject_code} - Section {code_section}")
                    
                    class_settings.append({
                        "subject_code": subject_code,
                        "code_section": code_section,
                        "time": time_range,
                        "room": room,
                        "college": college,
                        "program": program
                    })
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Generate button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button(
                    "Generate PDF Documents",
                    type="primary",
                    use_container_width=True
                ):
                    if not (gen_logsheet or gen_seatplan or gen_syllabi):
                        st.warning("Please select at least one document type to generate.")
                    elif not faculty_name:
                        st.warning("Please enter a faculty name.")
                    else:
                        with st.spinner("Generating PDFs... This may take a moment."):
                            try:
                                final_outputs = []
                                progress_bar = st.progress(0)
                                status_text = st.empty()
                                
                                for i, data in enumerate(all_data):
                                    status_text.text(f"Processing {data['filename']}...")
                                    
                                    students = data["students"]
                                    filename = os.path.splitext(data["filename"])[0]
                                    settings = class_settings[i]
                                    
                                    folder_path = os.path.join("outputs", filename)
                                    os.makedirs(folder_path, exist_ok=True)
                                    
                                    pdf_parts = []
                                    semester_str = f"{semester} | {term} | {school_year}"
                                    
                                    if gen_logsheet:
                                        logsheet_file = generate_logsheet_with_details(
                                            students,
                                            faculty_name,
                                            settings["subject_code"],
                                            settings["time"],
                                            semester_str,
                                            program_head,
                                            branch,
                                            subject_type
                                        )
                                        
                                        new_path = os.path.join(folder_path, "logsheet.pdf")
                                        os.replace(logsheet_file, new_path)
                                        pdf_parts.append(new_path)
                                    
                                    if gen_seatplan:
                                        semester_str = f"{term} | {semester} | {school_year}"
                                        seatplan_file = generate_seatplan(
                                            students,
                                            semester_str,
                                            settings["subject_code"],
                                            settings["code_section"],
                                            settings["time"],
                                            settings["room"],
                                            settings["college"],
                                            settings["program"],
                                            faculty_name,
                                            program_head,
                                            branch
                                        )
                                        
                                        new_path = os.path.join(folder_path, "seatplan.pdf")
                                        os.replace(seatplan_file, new_path)
                                        pdf_parts.append(new_path)
                                    
                                    if gen_syllabi:
                                        syllabi_file = generate_syllabi(
                                            students,
                                            teacher=faculty_name,
                                            subject=settings["subject_code"],
                                            code=settings["code_section"],
                                            term=settings["time"],
                                            semester=semester,
                                            branch=branch
                                        )
                                        
                                        new_path = os.path.join(folder_path, "syllabi.pdf")
                                        os.replace(syllabi_file, new_path)
                                        pdf_parts.append(new_path)
                                    
                                    # Merge PDFs
                                    if pdf_parts:
                                        merged_path = os.path.join(folder_path, f"{filename}_COMPLETE.pdf")
                                        
                                        def merge_pdfs(pdf_paths, output_path):
                                            merger = PdfMerger()
                                            for path in pdf_paths:
                                                if os.path.exists(path):
                                                    merger.append(path)
                                            merger.write(output_path)
                                            merger.close()
                                            return output_path
                                        
                                        merge_pdfs(pdf_parts, merged_path)
                                        final_outputs.append((filename, merged_path))
                                    
                                    progress_bar.progress((i + 1) / len(all_data))
                                
                                status_text.text("Generation complete!")
                                progress_bar.empty()
                                
                                # Store in session state for downloads tab
                                st.session_state.generation_complete = True
                                st.session_state.generated_files = final_outputs
                                
                                st.success("All PDF documents generated successfully!")
                                st.balloons()
                                
                            except Exception as e:
                                st.error(f"Error during generation: {str(e)}")
                                st.exception(e)
        
        with tab3:
            # Downloads section
            if st.session_state.generation_complete and st.session_state.generated_files:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<p class="card-header">Download Generated Documents</p>', unsafe_allow_html=True)
                
                st.success("Your documents are ready for download!")
                
                for idx, (class_name, file_path) in enumerate(st.session_state.generated_files):
                    with st.container():
                        col1, col2, col3 = st.columns([3, 1, 1])
                        
                        with col1:
                            st.markdown(f"**{class_name}**")
                        
                        with col2:
                            file_size = os.path.getsize(file_path) / 1024  # KB
                            st.markdown(f"`{file_size:.1f} KB`")
                        
                        with col3:
                            with open(file_path, "rb") as f:
                                st.download_button(
                                    label="Download",
                                    data=f.read(),
                                    file_name=os.path.basename(file_path),
                                    mime="application/pdf",
                                    key=f"download_{idx}"
                                )
                
                # Option to generate new documents
                if st.button("Generate New Documents", use_container_width=True):
                    st.session_state.generation_complete = False
                    st.session_state.generated_files = []
                    st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No documents have been generated yet. Please go to the Configuration tab to generate documents.")
    
    else:
        st.warning("No valid student data found in the uploaded files.")

else:
    with tab1:
        st.info("Please upload Excel files to begin")
    
    with tab2:
        st.info("Upload files first to access configuration")
    
    with tab3:
        st.info("Generate documents first to see downloads")

# Footer
st.markdown("""
<div class="footer">
    <p>© 2024 Life Support PDF Generator. All rights reserved.</p>
    <p>Version 1.0.0 | Made with love for Sir Buddy hehe</p>
</div>
""", unsafe_allow_html=True)