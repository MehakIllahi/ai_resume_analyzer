from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch


def generate_resume_pdf(file_path, resume_text):
    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    # -------- STYLES --------
    name_style = ParagraphStyle(
        "Name",
        fontSize=20,
        leading=24,
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
        spaceAfter=6,
    )

    title_style = ParagraphStyle(
        "Title",
        fontSize=11,
        alignment=TA_CENTER,
        spaceAfter=6,
    )

    contact_style = ParagraphStyle(
        "Contact",
        fontSize=9,
        alignment=TA_CENTER,
        spaceAfter=12,
    )

    section_style = ParagraphStyle(
        "Section",
        fontSize=11,
        fontName="Helvetica-Bold",
        spaceBefore=12,
        spaceAfter=6,
    )

    body_style = ParagraphStyle(
        "Body",
        fontSize=10,
        spaceAfter=4,
    )

    bullet_style = ParagraphStyle(
        "Bullet",
        fontSize=10,
        leftIndent=14,
        spaceAfter=3,
    )

    content = []

    # -------- CLEAN & SPLIT --------
    raw_lines = resume_text.split("\n")
    lines = [l.strip() for l in raw_lines if l.strip()]

    # -------- SAFE HEADER EXTRACTION --------
    name = lines[0] if len(lines) > 0 else "YOUR NAME"
    role = lines[1] if len(lines) > 1 else ""
    contact = lines[2] if len(lines) > 2 else ""

    content.append(Paragraph(name, name_style))

    if role:
        content.append(Paragraph(role, title_style))

    if contact:
        content.append(Paragraph(contact, contact_style))

    content.append(HRFlowable(width="100%", thickness=1))
    content.append(Spacer(1, 0.15 * inch))

    # -------- BODY --------
    body_lines = lines[3:] if len(lines) > 3 else []

    for line in body_lines:
        if line.isupper() and len(line) < 35:
            content.append(Spacer(1, 0.1 * inch))
            content.append(Paragraph(line, section_style))

        elif line.startswith("•"):
            content.append(Paragraph(line, bullet_style))

        else:
            content.append(Paragraph(line, body_style))

    doc.build(content)
