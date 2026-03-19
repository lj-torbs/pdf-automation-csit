import re
import math
from PyPDF2 import PdfReader, PdfWriter
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
import os
from copy import deepcopy

def format_name(full_name):
    """
    ALL CAPS formatting that preserves multi-word surnames
    Example: "DE JESUS KHALIL GONZAGA" -> "DE JESUS, KHALIL"
    """
    if not full_name or pd.isna(full_name):
        return ""
    
    name = str(full_name).strip().upper()
    
    multi_word_surnames = [
        'DE JESUS', 'DELOS SANTOS', 'DELA CRUZ', 'DE LOS REYES',
        'DELA ROSA', 'DE GUZMAN', 'DE LEON', 'DEL MUNDO',
        'DEL CASTILLO', 'DELA PENA', 'DE VERA', 'DE CASTRO', 'DE PALMA', 'DEL ROSARIO', 'DE LA CRUZ', 'DE LA ROSA', 'DE LA VERA', 'DE LA GUZMAN', 'DE LA LEON', 'DE LA PALMA'
    ]
    
    for surname_pattern in multi_word_surnames:
        if name.startswith(surname_pattern):
            surname = surname_pattern
            rest = name[len(surname_pattern):].strip().split()
            if rest:
                firstname = rest[0]
                return f"{surname}, {firstname}"
            else:
                return surname
    
    parts = name.split()
    if len(parts) == 1:
        return parts[0]
    elif len(parts) == 2:
        return f"{parts[0]}, {parts[1]}"
    else:
        surname = parts[0]
        firstname = parts[1]
        return f"{surname}, {firstname}"

def is_term_subject(subject_code):
    """
    Check if the subject code indicates a term
    Returns True if subject contains 'TERM' or matches term patterns
    """
    if not subject_code:
        return False
    
    subject_upper = subject_code.upper()
    term_patterns = ['TERM', '1ST', '2ND', '3RD', '4TH']
    return any(pattern in subject_upper for pattern in term_patterns)

def generate_logsheet_with_details(students, faculty_name="", subject_code="", time="", semester="", program_head="", branch="", subject_type=""):
    """Generate logsheet with header information and either student names or X marks"""
    
    writer = PdfWriter()
    
    is_term = subject_type == "Term"
    
    start_y = 642
    row_height = 20.4
    x_position = 53
    rows_per_page = 25
    
    # Grid coordinates for term subjects (similar to seatplan.py)
    cols_per_row = 10
    col_x_positions = [
        46,    # Column 1
        116,   # Column 2
        193,   # Column 3
        262,   # Column 4
        332,   # Column 5
        457,   # Column 6
        523,   # Column 7
        600,   # Column 8
        675,   # Column 9
        745,   # Column 10
    ]
    
    if len(students) <= 20:
        bottom_y = 180
        top_y = 248
    elif len(students) <= 40:
        bottom_y = 180
        top_y = 368
    else:
        bottom_y = 180
        top_y = 430
    
    rows_needed = math.ceil(len(students) / cols_per_row)
    if rows_needed > 1:
        row_height_grid = (top_y - bottom_y) / (rows_needed - 1)
    else:
        row_height_grid = 0
    
    # Header field coordinates
    faculty_x, faculty_y = 118, 720
    subject_x, subject_y = 118, 700
    time_x, time_y = 244, 700
    semester_x, semester_y = 410, 700
    program_head_x, program_head_y = 340, 75
    faculty_secondx, faculty_secondy = 90, 75

    if branch == "Main":
        branchx, branchy = 150, 778
    else:
        branchx, branchy = 205, 778
    
    template_path = "student examination.pdf"
    
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template file '{template_path}' not found!")
    
    
        
    else:
        total_pages = (len(students) + rows_per_page - 1) // rows_per_page
        
        for page_num in range(total_pages):
            page_start = page_num * rows_per_page
            page_end = min(page_start + rows_per_page, len(students))
            page_students = students[page_start:page_end]
            
            packet = BytesIO()
            c = canvas.Canvas(packet, pagesize=letter)
            
            c.setFont("Helvetica", 9)
            
            if page_num == 0 or page_num == 1:
                c.setFont("Helvetica", 10)
                if faculty_name:
                    c.drawString(faculty_x, faculty_y, f" {faculty_name}")
                    c.drawString(faculty_secondx, faculty_secondy, f" {faculty_name}")
                if subject_code:
                    c.drawString(subject_x, subject_y, f" {subject_code}")
                if time:
                    clean_time = re.sub(r"\s?(AM|PM)", "", time)
                    c.drawString(time_x, time_y, f" {clean_time}")
                if semester:
                    c.drawString(semester_x, semester_y, f" {semester}")
                if program_head:
                    c.drawString(program_head_x, program_head_y, f" {program_head}")
                if branch:
                    c.drawString(branchx, branchy, "✔                  Tagum")
            
            c.setFont("Helvetica", 10)
            x_mark_positions = [380, 430, 480, 530]
            for i, student in enumerate(page_students):
                y = start_y - (i * row_height)

                formatted_name = format_name(student)
                student_text = f"{formatted_name}"

                if len(student_text) > 50:
                    student_text = student_text[:47] + "..."

                c.drawString(x_position, y, student_text)

                if is_term:
                    c.setFont("Helvetica", 10)

                    for x_mark in x_mark_positions:
                        c.drawString(x_mark, y, "X")
            c.save()
            packet.seek(0)
            
            overlay = PdfReader(packet)
            template = PdfReader(template_path)
            page = deepcopy(template.pages[0])
            page.merge_page(overlay.pages[0])
            writer.add_page(page)
    
    output_file = "logsheet_complete.pdf"
    with open(output_file, "wb") as f:
        writer.write(f)
    
    return output_file

def generate_logsheet(students):
    """Generate simple logsheet with formatted names"""
    return generate_logsheet_with_details(students)

if __name__ == "__main__":
    test_names = [
        "DE JESUS KHALIL GONZAGA",
        "DELA CRUZ SIEGMON NORMAN LARA",
        "DELOS SANTOS JUAN CARLOS",
        "ALBITE RJ ALIWANAG",
        "DE LOS REYES MARIA TERESA",
        "VILLAVER DANICA MARIE MARDOQUIO"
    ]
    
    print("Testing name formatting:")
    for name in test_names:
        formatted = format_name(name)
        print(f"Original: {name}")
        print(f"Formatted: {formatted}")
        print("-" * 40)
    
    # Test the term subject functionality
    print("\nTesting term subject detection:")
    test_subjects = ["1ST TERM MATH", "2ND TERM SCIENCE", "REGULAR MATH 101", "TERM 3 ENGLISH"]
    for subject in test_subjects:
        print(f"{subject}: {'Is Term' if is_term_subject(subject) else 'Regular Subject'}")