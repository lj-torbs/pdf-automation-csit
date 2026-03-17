from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
import os

def create_coordinate_guide():
    """Creates a guide PDF with numbered lines to find exact coordinates"""
    
    # Check if template exists
    template_path = "student examination.pdf"
    if not os.path.exists(template_path):
        print(f"ERROR: Could not find {template_path}")
        return
    
    print(f"Found template: {template_path}")
    
    # Create a new PDF layer with coordinate markers
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)
    
    # Draw horizontal lines with Y-coordinates
    # Start from bottom (0) to top (letter height is 792 points)
    for y in range(500, 750, 10):  # Focus on the area where names might be
        if y % 20 == 0:  # Every 20 points, draw a line and number
            c.setStrokeColorRGB(0.8, 0.8, 0.8)  # Light gray
            c.line(50, y, 550, y)  # Horizontal line across the page
            c.setFillColorRGB(1, 0, 0)  # Red text
            c.drawString(10, y-5, f"y={y}")
    
    # Draw vertical lines with X-coordinates
    for x in range(40, 200, 10):  # Focus on left side where names go
        if x % 20 == 0:  # Every 20 points
            c.setStrokeColorRGB(0.8, 0.8, 0.8)
            c.line(x, 500, x, 750)
            c.setFillColorRGB(0, 0, 1)  # Blue text
            c.drawString(x-5, 740, f"x={x}")
    
    # Add some sample student names to test positioning
    c.setFillColorRGB(0, 0, 0)  # Black text
    test_names = [
        "TEST NAME 1",
        "TEST NAME 2",
        "TEST NAME 3",
        "TEST NAME 4",
        "TEST NAME 5"
    ]
    
    # Try different starting Y positions
    test_start_y = 638
    test_row_height = 21
    
    for i, name in enumerate(test_names):
        y = test_start_y - (i * test_row_height)
        c.setFillColorRGB(0, 0.5, 0)  # Dark green
        c.drawString(60, y, f"[{i+1}] {name}")
    
    c.save()
    
    # Move to beginning of buffer
    packet.seek(0)
    
    # Read the overlay and template
    overlay = PdfReader(packet)
    template = PdfReader(template_path)
    
    # Create output PDF
    writer = PdfWriter()
    
    # For each page in template (usually just one)
    for page_num in range(len(template.pages)):
        page = template.pages[page_num]
        page.merge_page(overlay.pages[0])
        writer.add_page(page)
    
    # Save the guide
    output_path = "coordinate_guide.pdf"
    with open(output_path, "wb") as f:
        writer.write(f)
    
    print(f"\n✅ Created {output_path}")
    print("\n📏 Instructions:")
    print("1. Open coordinate_guide.pdf")
    print("2. Look for the red horizontal lines with Y-coordinates")
    print("3. Find which Y-coordinate aligns with the first row's top")
    print("4. Look for blue vertical lines with X-coordinates")
    print("5. Find which X-coordinate aligns with where names should start")
    print("6. The green text shows where names would appear with:")
    print(f"   - start_y = {test_start_y}")
    print(f"   - row_height = {test_row_height}")
    print(f"   - x_position = 60")
    print("\nAdjust these values based on what you see!")

def create_precision_guide():
    """Creates a more precise guide focusing on the table area"""
    
    template_path = "student_examination.pdf"
    
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)
    
    # Draw a grid in the table area
    # Based on typical table layouts, let's scan the area
    for row in range(30):  # 30 potential rows
        y = 650 - (row * 20)  # Test every 20 points from 650 down
        
        # Draw small markers
        c.setFillColorRGB(0.5, 0, 0.5)  # Purple
        c.drawString(10, y-3, f"R{row+1}")
        
        # Draw vertical markers for columns
        c.setFillColorRGB(0, 0.5, 0.5)  # Teal
        c.drawString(50, y-3, "|")
        c.drawString(100, y-3, "|")
        c.drawString(150, y-3, "|")
        c.drawString(200, y-3, "|")
    
    c.save()
    packet.seek(0)
    
    overlay = PdfReader(packet)
    template = PdfReader(template_path)
    
    writer = PdfWriter()
    page = template.pages[0]
    page.merge_page(overlay.pages[0])
    writer.add_page(page)
    
    with open("precision_guide.pdf", "wb") as f:
        writer.write(f)
    
    print("✅ Created precision_guide.pdf for detailed alignment")

if __name__ == "__main__":
    print("🔍 PDF Coordinate Finder Tool")
    print("=" * 40)
    create_coordinate_guide()
    create_precision_guide()
    print("\n✨ Now open both generated PDFs to find your exact coordinates!")
    print("Look for the line that aligns perfectly with where the first name should go")