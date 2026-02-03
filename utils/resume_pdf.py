from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER


# ---------------- AI SKILL GROUPING ----------------
def group_skills(skills):
    categories = {
        "Programming Languages": ["c", "c++", "java", "python", "javascript"],
        "Frontend": ["html", "css", "bootstrap", "react", "angular"],
        "Backend": ["spring", "spring boot", "node", "express", "django","python"],
        "Databases": ["mysql", "postgresql", "mongodb"],
        "Tools & Technologies": ["git", "github", "aws", "docker", "jenkins", "rest"]
    }

    grouped = {k: [] for k in categories}
    grouped["Other"] = []

    for skill in skills:
        added = False
        s = skill.lower()
        for category, keywords in categories.items():
            if any(k in s for k in keywords):
                grouped[category].append(skill)
                added = True
                break
        if not added:
            grouped["Other"].append(skill)

    return {k: v for k, v in grouped.items() if v}


# ---------------- PDF GENERATOR ----------------
def generate_resume_pdf(path, resume_text):
    doc = SimpleDocTemplate(
        path,
        pagesize=A4,
        leftMargin=50,
        rightMargin=50,
        topMargin=40,
        bottomMargin=40
    )

    story = []

    # ---------------- STYLES ----------------
    name_style = ParagraphStyle(
        "Name",
        fontName="Times-Bold",
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=6
    )

    contact_style = ParagraphStyle(
        "Contact",
        fontSize=9,
        alignment=TA_CENTER,
        spaceAfter=10
    )

    section_style = ParagraphStyle(
        "Section",
        fontName="Times-Bold",
        fontSize=11,
        spaceBefore=12,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        "Body",
        fontSize=10,
        leading=13
    )

    bold_style = ParagraphStyle(
        "Bold",
        parent=body_style,
        fontName="Times-Bold"
    )

    # ---------------- PARSE TEXT ----------------
    lines = [l.strip() for l in resume_text.splitlines() if l.strip()]

    # ---------------- HEADER ----------------
    story.append(Paragraph(lines[0], name_style))
    story.append(Paragraph(lines[1], contact_style))
    story.append(HRFlowable(width="100%", thickness=0.8))
    story.append(Spacer(1, 8))

    i = 2
    current_section = None
    skills_raw = []

    while i < len(lines):
        line = lines[i]

        # SECTION HEADERS
        if line.isupper():
            current_section = line

            story.append(Spacer(1, 8))
            story.append(Paragraph(line, section_style))
            story.append(HRFlowable(width="100%", thickness=0.6))
            story.append(Spacer(1, 6))

            i += 1
            continue

        # SKILLS COLLECTION
        if current_section == "TECHNICAL SKILLS":
            skills_raw.extend([s.strip() for s in line.split(",")])
            i += 1
            continue

        # EXPERIENCE → bold company + role + timeline
        if current_section == "EXPERIENCE" and "|" in line:
            story.append(Paragraph(line, bold_style))

        # EDUCATION → always normal text
        elif current_section == "EDUCATION":
            story.append(Paragraph(line, body_style))

        # Everything else
        else:
            story.append(Paragraph(line, body_style))

        i += 1

    # ---------------- RENDER SKILLS (AT END) ----------------
    if skills_raw:
        story.append(Spacer(1, 8))
        story.append(Paragraph("TECHNICAL SKILLS", section_style))
        story.append(HRFlowable(width="100%", thickness=0.6))
        story.append(Spacer(1, 6))

        grouped = group_skills(skills_raw)

        for category, items in grouped.items():
            story.append(
                Paragraph(
                    f"<b>{category}:</b> {', '.join(sorted(items))}",
                    body_style
                )
            )
            story.append(Spacer(1, 4))

    doc.build(story)
