import os
import streamlit as st
import pandas as pd
from generators.logsheet import generate_logsheet_with_details
from generators.seatplan import generate_seatplan
from generators.syllabi import generate_syllabi
#streamlit run app.py
st.title("LIFE SUPPORT PDF GENERATOR")
st.markdown("Upload Excel files to generate the HOLY TRINITY DOCUMENTS")

uploaded_files = st.file_uploader(
    "Choose Excel files",
    type=['xlsx', 'xls'],
    accept_multiple_files=True
)

if uploaded_files:
    all_data = []

    for uploaded_file in uploaded_files:
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

                all_data.append({
                    "filename": uploaded_file.name,
                    "students": students
                })
            else:
                st.error(f"{uploaded_file.name} has no valid name column")

        except Exception as e:
            st.error(f"Error reading {uploaded_file.name}: {str(e)}")


    if all_data:
        st.success(f"Loaded {len(all_data)} class list(s)")

        with st.expander("Preview per file"):
            for data in all_data:
                st.write(f"**{data['filename']}** ({len(data['students'])} students)")
                preview_df = pd.DataFrame({
                    "#": range(1, len(data["students"]) + 1),
                    "Student Name": data["students"]
                })
                st.dataframe(preview_df, use_container_width=True)

        st.subheader("Select Documents to Generate")

        select_all = st.checkbox("Select All")

        col_a, col_b, col_c = st.columns(3)

        with col_a:
            gen_logsheet = st.checkbox("Logsheet", value=select_all)

        with col_b:
            gen_seatplan = st.checkbox("Seat Plan", value=select_all)

        with col_c:
            gen_syllabi = st.checkbox("Syllabi", value=select_all)

        st.subheader("Header Information (Optional)")

        col1, col2 = st.columns(2)

        with col1:
            faculty_name = st.text_input("Faculty Name")

        with col2:
            semester = st.text_input("Sem/Term/S.Y.")

        st.subheader("Per Class Settings")

        class_settings = []

        for i, data in enumerate(all_data):
            with st.expander(f"Settings for {data['filename']}"):
                col1, col2, col3 = st.columns(3)

                with col1:
                    subject_code = st.text_input(f"Subject Code", key=f"sub_{i}")

                with col2:
                    code_section = st.text_input(f"Code/Section", key=f"sec_{i}")

                with col3:
                    time = st.text_input(f"Time", key=f"time_{i}")

                col4, col5, col6 = st.columns(3)

                with col4:
                    room = st.text_input("Room", key=f"room_{i}")

                with col5:
                    college = st.text_input("College", key=f"col_{i}")

                with col6:
                    program = st.text_input("Program", key=f"prog_{i}")

                class_settings.append({
                    "subject_code": subject_code,
                    "code_section": code_section,
                    "time": time,
                    "room": room,
                    "college": college,
                    "program": program
                })

        # GENERATE
        if st.button("Generate PDF", type="primary"):
            if not (gen_logsheet or gen_seatplan or gen_syllabi):
                st.warning("Please select at least one document.")
            else:
                with st.spinner("Generating PDFs..."):
                    try:
                        generated_files = []

                        for i, data in enumerate(all_data):
                            students = data["students"]
                            filename = os.path.splitext(data["filename"])[0]
                            settings = class_settings[i]

                            folder_path = os.path.join("outputs", filename)
                            os.makedirs(folder_path, exist_ok=True)

                            if gen_logsheet:
                                st.info(f"Generating Logsheet for {filename}...")
                                logsheet_file = generate_logsheet_with_details(
                                    students,
                                    faculty_name,
                                    settings["subject_code"],
                                    settings["time"],
                                    semester
                                )

                                new_path = os.path.join(folder_path, "logsheet.pdf")
                                os.replace(logsheet_file, new_path)
                                generated_files.append(("Logsheet", new_path))

                            if gen_seatplan:
                                st.info(f"Generating Seat Plan for {filename}...")
                                seatplan_file = generate_seatplan(
                                    students,
                                    semester,
                                    settings["subject_code"],
                                    settings["code_section"],
                                    settings["time"],
                                    settings["room"],
                                    settings["college"],
                                    settings["program"],
                                    faculty_name
                                )

                                new_path = os.path.join(folder_path, "seatplan.pdf")
                                os.replace(seatplan_file, new_path)
                                generated_files.append(("Seat Plan", new_path))

                            if gen_syllabi:
                                st.info(f"Generating Syllabi for {filename}...")
                                syllabi_file = generate_syllabi(
                                    students,
                                    teacher=faculty_name,
                                    subject=settings["subject_code"],
                                    code=settings["code_section"],
                                    term=settings["time"],
                                    semester=semester
                                )

                                new_path = os.path.join(folder_path, "syllabi.pdf")
                                os.replace(syllabi_file, new_path)
                                generated_files.append(("Syllabi", new_path))

                        st.success("All PDFs generated successfully")

                        for idx, (doc_name, file_path) in enumerate(generated_files):
                            with open(file_path, "rb") as f:
                                st.download_button(
                                    label=f"Download {doc_name} ({os.path.basename(file_path)})",
                                    data=f,
                                    file_name=os.path.basename(file_path),
                                    mime="application/pdf",
                                    use_container_width=True,
                                    key=f"{doc_name}_{idx}"
                                )

                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                        st.exception(e)

else:
    st.info("Please upload Excel files to begin")