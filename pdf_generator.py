from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
from io import BytesIO
import base64
from PIL import Image
import qrcode
from reportlab.lib.colors import HexColor
import tempfile
import os

def generate_certificate_pdf(certificate_data):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Set up styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=HexColor('#2E3A59'),
        spaceAfter=30,
        alignment=1
    )
    name_style = ParagraphStyle(
        'CustomName',
        parent=styles['Heading2'],
        fontSize=20,
        textColor=HexColor('#1B5E20'),
        spaceAfter=20,
        alignment=1
    )
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=14,
        textColor=HexColor('#263238'),
        spaceAfter=10,
        alignment=1
    )
    
    # Draw a light background
    c.setFillColor(HexColor('#F5F7FA'))
    c.rect(0, 0, 612, 792, fill=1, stroke=0)
    
    # Draw a colored border
    c.setStrokeColor(HexColor('#1976D2'))
    c.setLineWidth(6)
    c.rect(40, 40, 532, 712, fill=0, stroke=1)
    
    # Add title
    title = Paragraph("CERTIFICATE OF ACHIEVEMENT", title_style)
    title.wrapOn(c, 500, 50)
    title.drawOn(c, 56, 700)
    
    # Add recipient name
    name_text = f"Recipient: {certificate_data.get('recipient_name', '')}" 
    name = Paragraph(name_text, name_style)
    name.wrapOn(c, 500, 30)
    name.drawOn(c, 56, 640)

    # Add course name
    course_text = f"Course: {certificate_data.get('course_name', '')}"
    course = Paragraph(course_text, body_style)
    course.wrapOn(c, 500, 30)
    course.drawOn(c, 56, 610)

    # Add date
    date_text = f"Issued on: {certificate_data.get('issue_date', '')}"
    date = Paragraph(date_text, body_style)
    date.wrapOn(c, 500, 30)
    date.drawOn(c, 56, 580)

    # Add certificate ID
    id_text = f"Certificate ID: {certificate_data.get('certificate_id', '')}"
    id_para = Paragraph(id_text, body_style)
    id_para.wrapOn(c, 500, 30)
    id_para.drawOn(c, 56, 550)

    # Add the full generated content
    content_text = certificate_data.get('content', '')
    content_para = Paragraph(content_text.replace('\n', '<br/>'), body_style)
    content_para.wrapOn(c, 500, 200)
    content_para.drawOn(c, 56, 450)
    
    # Add QR code at bottom right
    if certificate_data.get('qr_code'):
        temp_file = None
        try:
            qr_data = base64.b64decode(certificate_data['qr_code'])
            qr_image = Image.open(BytesIO(qr_data))
            
            # Save to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                qr_image.save(temp_file, format='PNG')
                temp_file_path = temp_file.name
                
            # Draw the image from the temporary file
            c.drawImage(temp_file_path, 442, 70, width=120, height=120, preserveAspectRatio=True, mask='auto')
            
        except Exception as e:
            print(f"Error adding QR code to PDF: {e}")
            raise e
        finally:
            # Clean up the temporary file
            if temp_file and os.path.exists(temp_file.name):
                os.remove(temp_file.name)
    
    c.save()
    buffer.seek(0)
    return buffer 