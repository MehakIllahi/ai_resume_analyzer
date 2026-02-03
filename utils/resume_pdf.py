from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle

def generate_resume_pdf(path, text):
    """
    Generate a simple resume PDF from a string.
    """
    doc = SimpleDocTemplate(path, pagesize=A4, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
    story = []

    normal_style = ParagraphStyle('Normal', fontSize=10, leading=12)

    for line in str(text).splitlines():
        if not line.strip():
            story.append(Spacer(1, 6))
        else:
            story.append(Paragraph(line.strip(), normal_style))

    doc.build(story)
