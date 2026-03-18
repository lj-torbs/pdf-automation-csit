from PyPDF2 import PdfReader, PdfWriter
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
import os
from copy import deepcopy
import math

def format_name_seatplan(full_name):
    """
    Format name as:
    SURNAME,
    FIRSTNAME
    """
    if not full_name or pd.isna(full_name):
        return ""
    
    name = str(full_name).strip().upper()
    
    multi_word_surnames = [
        'DE JESUS', 'DELOS SANTOS', 'DELA CRUZ', 'DE LOS REYES',
        'DELA ROSA', 'DE GUZMAN', 'DE LEON', 'DEL MUNDO',
        'DEL CASTILLO', 'DELA PENA', 'DE VERA', 'DE CASTRO', 'DEL ROSARIO'
    ]
    
    for surname_pattern in multi_word_surnames:
        if name.startswith(surname_pattern):
            surname = surname_pattern
            rest = name[len(surname_pattern):].strip().split()
            if rest:
                firstname = rest[0]
                return f"{surname},\n{firstname}"
            else:
                return surname
    
    parts = name.split()
    
    if len(parts) == 1:
        return parts[0]
    elif len(parts) >= 2:
        surname = parts[0]
        firstname = parts[1]
        return f"{surname},\n{firstname}"

def generate_seatplan(students, semester="", subject="", code_section="", 
                      time="", room="", college="", program="", faculty_name=""):
    """
    Generate seat plan PDF with student names in a 10x? grid
    Fills left to right, bottom to top
    """
    
    writer = PdfWriter()
    
    template_path = "seat plan.pdf"
    
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template file '{template_path}' not found!")
    
    cols_per_row = 10
    
    total_students = len(students)
    rows_needed = math.ceil(total_students / cols_per_row)
    
    col_x_positions = [ 
        46,    # Column 1
        115,   # Column 2
        193,   # Column 3
        262,   # Column 4
        332,   # Column 5
        457,   # Column 6
        523,   # Column 7
        600,   # Column 8
        675,   # Column 9
        745,   # Column 10
    ]
    
    bottom_y = 180        
    top_y = 368          
    
    if rows_needed > 1:
        row_height = (top_y - bottom_y) / (rows_needed - 1)
    else:
        row_height = 0
    
    
   
    header_coords = {
        'semester': (125, 475),     
        'subject': (85, 116),         
        'code_section': (253, 116),  
        'time': (85, 98),            
        'room': (240, 98),           
        'college': (85, 80),         
        'program': (250, 80),        
        'faculty_name': (500, 80),      
    }
    
    packet = BytesIO()
    template = PdfReader(template_path)
    page = template.pages[0]

    
    width = float(page.mediabox.width)
    height = float(page.mediabox.height)

    c = canvas.Canvas(packet, pagesize=(width, height))
    
    c.setFont("Helvetica", 13) 
    
    c.setFont("Helvetica", 10)
    
    if semester:
        c.drawString(header_coords['semester'][0], header_coords['semester'][1], f"{semester}")
    if subject:
        c.drawString(header_coords['subject'][0], header_coords['subject'][1], f"{subject}")
    if code_section:
        c.drawString(header_coords['code_section'][0], header_coords['code_section'][1], f"{code_section}")
    if time:
        c.drawString(header_coords['time'][0], header_coords['time'][1], f"{time}")
    if room:
        c.drawString(header_coords['room'][0], header_coords['room'][1], f"{room}")
    if college:
        c.drawString(header_coords['college'][0], header_coords['college'][1], f"{college}")
    if program:
        c.drawString(header_coords['program'][0], header_coords['program'][1], f"{program}")
    if faculty_name:
        c.drawString(header_coords['faculty_name'][0], header_coords['faculty_name'][1], f"{faculty_name}")
    
    c.setFont("Helvetica", 9) 
    
    for i, student in enumerate(students):
        row_from_bottom = i // cols_per_row           
        col = i % cols_per_row                        
        
        y = bottom_y + (row_from_bottom * row_height)
    
        x = col_x_positions[col]
        
        formatted_name = format_name_seatplan(student)
        
        student_number = i + 1
        student_text = f"{formatted_name}"
        
        max_width = 150 

        while c.stringWidth(student_text, "Helvetica", 10) > max_width:
            student_text = student_text[:-1]

        lines = student_text.split("\n")

        for j, line in enumerate(lines):
            c.drawCentredString(x + 20, y - (j * 8), line)
    
    c.save()
    packet.seek(0)
    

    overlay = PdfReader(packet)
    template = PdfReader(template_path)
    
    page = deepcopy(template.pages[0])
    page.merge_page(overlay.pages[0])
    writer.add_page(page)
    
    output_file = "seatplan_complete.pdf"
    with open(output_file, "wb") as f:
        writer.write(f)
    
    return output_file

def generate_seatplan_simple(students):
    """Generate simple seat plan with just student names"""
    return generate_seatplan(students)

if __name__ == "__main__":
    test_students = [f"Student {i}" for i in range(1, 31)]
    generate_seatplan(test_students, 
                     semester="1st Sem 2023-2024",
                     subject="MATH 101",
                     faculty_name="Dr. Smith")