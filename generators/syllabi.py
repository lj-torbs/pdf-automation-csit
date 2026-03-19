from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
from copy import deepcopy
import os
import pandas as pd


def generate_syllabi(students, teacher="", subject="", code="", term="", semester="", branch=""):
    writer = PdfWriter()

    template_path = "syllabicontrol.pdf" 

    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template file '{template_path}' not found!")

    # Layout (adjust if needed)
    start_y = 602
    row_height = 23.9
    x_name = 70   # NAME column
    rows_per_page = 22

    # Header positions (adjust if needed)
    teacher_x, teacher_y = 120, 705
    subject_x, subject_y = 405, 705
    code_x, code_y = 110, 677
    term_x, term_y = 240, 677
    semester_x, semester_y = 405, 677
    if branch == "Main":
        branchx, branchy = 262, 765
    else:
        branchx, branchy = 319, 765

    total_pages = (len(students) + rows_per_page - 1) // rows_per_page

    for page_num in range(total_pages):
        page_start = page_num * rows_per_page
        page_end = min(page_start + rows_per_page, len(students))
        page_students = students[page_start:page_end]

        packet = BytesIO()
        c = canvas.Canvas(packet, pagesize=letter)

        # HEADER
        c.setFont("Helvetica", 10)
        if teacher:
            c.drawString(teacher_x, teacher_y, teacher)
        if subject:
            c.drawString(subject_x, subject_y, subject)
        if code:
            c.drawString(code_x, code_y, code)
        if term:
            c.drawString(term_x, term_y, term)
        if semester:
            c.drawString(semester_x, semester_y, semester)
        if branch:
            c.drawString(branchx, branchy, "✔                Tagum")

        # STUDENT NAMES (FULL, NO FORMAT)
        c.setFont("Helvetica-Bold", 10)

        for i, student in enumerate(page_students):
            y = start_y - (i * row_height)

            # FULL NAME, CLEANED ONLY
            name = str(student).strip().upper()

            # Prevent overflow
            if len(name) > 40:
                name = name[:37] + "..."

            c.drawString(x_name, y, name)

        c.save()
        packet.seek(0)

        overlay = PdfReader(packet)
        template = PdfReader(template_path)

        page = deepcopy(template.pages[0])
        page.merge_page(overlay.pages[0])
        writer.add_page(page)

    output_file = "syllabi_complete.pdf"

    with open(output_file, "wb") as f:
        writer.write(f)

    return output_file