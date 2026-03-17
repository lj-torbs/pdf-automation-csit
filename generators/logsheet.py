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
        'DEL CASTILLO', 'DELA PENA', 'DE VERA', 'DE CASTRO'
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
    
def generate_logsheet_with_details(students, faculty_name="", subject_code="", time="", semester=""):
    """Generate logsheet with header information and student names"""
    
    writer = PdfWriter()
    
    # Student name coordinates
    start_y = 642
    row_height = 20.4
    x_position = 53
    rows_per_page = 25
    
    # Header field coordinates
    faculty_x, faculty_y = 118, 720
    subject_x, subject_y = 118, 700
    time_x, time_y = 260, 700
    semester_x, semester_y = 410, 700
    
    template_path = "student examination.pdf"
    
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template file '{template_path}' not found!")
    
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
            if subject_code:
                c.drawString(subject_x, subject_y, f" {subject_code}")
            if time:
                c.drawString(time_x, time_y, f" {time}")
            if semester:
                c.drawString(semester_x, semester_y, f" {semester}")
        
        c.setFont("Helvetica", 9)
        for i, student in enumerate(page_students):
            y = start_y - (i * row_height)
            
            formatted_name = format_name(student)
            
            student_text = f"{formatted_name}"
            
            if len(student_text) > 50:
                student_text = student_text[:47] + "..."
            
            c.drawString(x_position, y, student_text)
        
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