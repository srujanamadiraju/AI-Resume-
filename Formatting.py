import re
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER

def clean_text(text):
    """Remove stars, extra colons, dashes, and unnecessary symbols."""
    return re.sub(r"[\*\*:]+", "", text).strip().replace("------", "")

def parse_resume_text(text):
    """
    Parses raw text and extracts structured sections dynamically.
    Returns a dictionary of sections with clean data.
    """
    sections = {}
    lines = [clean_text(line.strip()) for line in text.strip().split("\n") if line.strip()]
    
    current_section = None
    for line in lines:
        line = line.lstrip("•* ")  # Remove bullet points or stars at the beginning
        
        # Detect section headers (uppercase words without leading bullets)
        if re.match(r"^[A-Z][A-Za-z ]+$", line):
            current_section = line
            sections[current_section] = []
        elif current_section:
            sections[current_section].append(line)
    
    return sections

from reportlab.lib import colors

def generate_resume(text, filename="resume.pdf"):
    """
    Generates a structured resume PDF from dynamically generated text.
    """
    sections = parse_resume_text(text)
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()

    # Custom styles
    name_style = ParagraphStyle(name="Name", fontSize=20, alignment=TA_CENTER, spaceAfter=12, bold=True)
    section_style = ParagraphStyle(name="Section", fontSize=16, spaceAfter=8, bold=True, textColor=colors.darkblue)
    normal_style = ParagraphStyle(name="Normal", fontSize=12, spaceAfter=6)
    bold_style = ParagraphStyle(name="Bold", fontSize=12, spaceAfter=6, fontName="Helvetica-Bold")
    bullet_style = ParagraphStyle(name="Bullet", fontSize=12, leftIndent=20, spaceAfter=4)

    content = []

    # Extract Name
    name = list(sections.keys())[0] if sections else ""
    if name:
        content.append(Paragraph(name, name_style))
        content.append(Spacer(1, 14))
        sections.pop(name, None)  # Remove name from sections

    # Extract Contact Information
    contact_info = sections.pop("Contact Information", [])
    if contact_info:
        contact_text = " | ".join(contact_info)
        content.append(Paragraph(contact_text, normal_style))
        content.append(Spacer(1, 14))

    # Add remaining sections with better formatting
    for section, details in sections.items():
        content.append(Paragraph(section, section_style))  # Section header in bold and dark blue
        content.append(Spacer(1, 8))

        if section == "Education":
            # Bold university name
            for line in details:
                content.append(Paragraph(f"<b>{line}</b>", bold_style))
        elif section == "Skills":
            # Use bullet points for skills
            for skill in details:
                content.append(Paragraph(f"• {skill}", bullet_style))
        else:
            paragraph_text = " ".join(details)  # Ensure text is continuous
            content.append(Paragraph(paragraph_text, normal_style))

        content.append(Spacer(1, 13))  # Space between sections

    # Ensure there is content before building
    if not content:
        raise ValueError("Error: No valid content to generate the resume.")

    # Build and save PDF
    try:
        doc.build(content)
        print(f"✅ Resume saved successfully as: {filename}")
    except Exception as e:
        print(f"❌ Error generating resume: {e}")

    return filename

file = generate_resume(resume_text)  # run this in another cell and see the resume.pdf output in the same directory as the nb
