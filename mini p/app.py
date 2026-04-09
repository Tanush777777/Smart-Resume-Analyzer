# ...existing code...
from flask import Flask, request, jsonify, render_template, send_file
from werkzeug.utils import secure_filename
from io import BytesIO
import os
import re
import datetime
from fpdf import FPDF
from PyPDF2 import PdfReader
import docx

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_pdf(path):
    try:
        reader = PdfReader(path)
        text = []
        for p in reader.pages:
            txt = p.extract_text()
            if txt:
                text.append(txt)
        return "\n".join(text)
    except Exception:
        return ""


def extract_text_from_docx(path):
    try:
        doc = docx.Document(path)
        return "\n".join([p.text for p in doc.paragraphs])
    except Exception:
        return ""


def extract_text_from_file(path, filename):
    ext = filename.rsplit(".", 1)[1].lower()
    if ext == "pdf":
        return extract_text_from_pdf(path)
    elif ext == "docx":
        return extract_text_from_docx(path)
    else:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()


def find_emails(text):
    return re.findall(r"[\w\.-]+@[\w\.-]+\.\w+", text)


def find_phones(text):
    return re.findall(r"\+?\d[\d\-\s]{7,}\d", text)


def find_skills(text):
    # Basic list; extend as needed
    skills_list = ["python", "flask", "sql", "javascript", "react", "docker", "aws", "kubernetes", "c#", "java"]
    found = set()
    words = re.findall(r"\w+", text.lower())
    for s in skills_list:
        if s.lower() in words:
            found.add(s.title())
    return list(found)


def find_experience_years(text):
    m = re.search(r"(\d+)\+?\s*(?:years|yrs|year)", text, re.IGNORECASE)
    if m:
        return int(m.group(1))
    return 0


def split_sections(text):
    # Naive section splits by headings
    sections = {}
    headings = ["summary", "experience", "education", "skills"]
    lower_text = text.lower()
    for h in headings:
        idx = lower_text.find(h)
        if idx != -1:
            # take 250 chars after heading
            sections[h] = text[idx : idx + 250].strip()
    return sections


@app.route("/")
def index():
    return render_template("landing.html")


@app.route("/analysis")
def analysis():
    return render_template("analysis.html")


@app.route("/templates")
def templates_page():
    return render_template("templates.html")


@app.route("/jobs")
def jobs_page():
    return render_template("jobs.html")


@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    # Accept file or JSON with text
    file = request.files.get("file")
    text = ""
    filename = None
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(path)
        text = extract_text_from_file(path, filename)
    else:
        # fallback to direct text field for testing
        text = request.form.get("text") or (request.json and request.json.get("text")) or ""

    emails = find_emails(text)
    phones = find_phones(text)
    skills = find_skills(text)
    years = find_experience_years(text)
    sections = split_sections(text)
    word_count = len(re.findall(r"\w+", text))
    char_count = len(text)

    # Very simple "ATS score" simulation: skill hits and length
    ats_score = min(100, 40 + len(skills) * 15 + (0 if word_count < 200 else 10))

    response = {
        "ats_score": ats_score,
        "contact_info": {"emails": emails, "phones": phones},
        "skills": skills,
        "years_experience": years,
        "mentioned_titles": [],  # naive: left blank
        "sections": sections,
        "suggestions": [{"type": "info", "title": "Add more quantifiable results", "message": "Use numbers and metrics."}],
        "job_suggestions": [],
        "word_count": word_count,
        "character_count": char_count,
        "analysis_date": datetime.datetime.utcnow().isoformat() + "Z",
    }
    return jsonify(response)


@app.route("/api/job-suggestions", methods=["POST"])
def api_job_suggestions():
    # Accept a resume file or text and return simple job suggestions
    file = request.files.get("file")
    text = ""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(path)
        text = extract_text_from_file(path, filename)
    else:
        text = request.form.get("text") or (request.json and request.json.get("text")) or ""

    skills = find_skills(text)
    jobs = []
    if "Python" in skills or "Flask" in skills:
        jobs.append(
            {
                "title": "Backend Software Engineer",
                "description": "Work on API development and backend systems.",
                "companies": ["Acme Inc", "Globex Corp"],
                "match_score": 90,
                "salary_range": "$80k-$130k",
                "category": "Engineering",
                "remote": True,
            }
        )
    if "React" in skills or "JavaScript" in skills:
        jobs.append(
            {
                "title": "Frontend Engineer",
                "description": "Build UI features and frontend apps.",
                "companies": ["TechSoft", "DesignHub"],
                "match_score": 85,
                "salary_range": "$70k-$120k",
                "category": "Engineering",
                "remote": False,
            }
        )
    summary = {"skills_count": len(skills), "experience_years": find_experience_years(text)}
    return jsonify({"analysis_summary": summary, "job_suggestions": jobs})


def safe_text(text, max_length=200):
    """Safely convert text to PDF-compatible string"""
    if not text:
        return ""
    try:
        text_str = str(text)[:max_length]
        # Replace problematic characters that aren't supported by standard fonts
        # Replace bullet points with dashes
        text_str = text_str.replace('•', '-').replace('\u2022', '-')
        # Replace other common Unicode characters
        text_str = text_str.replace('\u2013', '-').replace('\u2014', '--')  # En/em dashes
        text_str = text_str.replace('\u2018', "'").replace('\u2019', "'")  # Smart quotes
        text_str = text_str.replace('\u201C', '"').replace('\u201D', '"')  # Smart quotes
        text_str = text_str.replace('\u2026', '...')  # Ellipsis
        # Try latin-1 encoding first
        text_str = text_str.encode('latin-1', 'replace').decode('latin-1')
        return text_str
    except:
        try:
            # Fallback to ASCII
            text_str = str(text)[:max_length]
            text_str = text_str.replace('•', '-').replace('\u2022', '-')
            return text_str.encode('ascii', 'ignore').decode('ascii')
        except:
            return ""

def add_section_header(pdf, text, page_width=190):
    """Add a styled section header"""
    pdf.set_fill_color(70, 130, 180)  # Steel blue
    pdf.set_text_color(255, 255, 255)  # White text
    pdf.set_font("Arial", "B", 14)
    pdf.cell(page_width, 10, safe_text(text), ln=True, fill=True, align='L')
    pdf.set_text_color(0, 0, 0)  # Reset to black
    pdf.ln(3)

def add_key_value(pdf, key, value, page_width=190, key_width=60):
    """Add a key-value pair with formatting"""
    pdf.set_font("Arial", "B", 10)
    pdf.cell(key_width, 7, safe_text(key + ":"), border=0, align='L')
    pdf.set_font("Arial", "", 10)
    value_str = safe_text(value, 500)
    # Calculate if we need multiple lines
    if len(value_str) > 50:
        pdf.ln()
        pdf.set_x(15)  # Indent for wrapped values
        pdf.multi_cell(page_width - 10, 6, value_str, align='L')
    else:
        pdf.cell(page_width - key_width, 7, value_str, ln=True, align='L')
    pdf.ln(2)

def add_score_box(pdf, score, page_width=190):
    """Add a visual score box"""
    # Determine color based on score
    if score >= 80:
        r, g, b = 34, 139, 34  # Green
    elif score >= 60:
        r, g, b = 255, 165, 0  # Orange
    else:
        r, g, b = 220, 20, 60  # Red
    
    pdf.set_fill_color(r, g, b)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 24)
    score_text = f"{score}%"
    box_width = 50
    box_height = 20
    x_pos = (page_width - box_width) / 2 + 10
    pdf.set_xy(x_pos, pdf.get_y())
    pdf.cell(box_width, box_height, score_text, border=1, fill=True, align='C', ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)

def make_pdf_bytes(title, data):
    """Create a detailed, styled PDF report from analysis data"""
    pdf = FPDF()
    pdf.add_page()
    
    # Page dimensions
    page_width = 190
    margin = 10
    
    # Header with title
    pdf.set_fill_color(70, 130, 180)  # Steel blue
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 20)
    pdf.cell(page_width, 15, safe_text(title, 100), ln=True, fill=True, align='C')
    pdf.ln(5)
    
    # Reset colors
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "", 10)
    
    # Date
    gen_date = data.get('generated_at', datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"))
    pdf.set_font("Arial", "I", 9)
    pdf.cell(page_width, 5, f"Generated: {safe_text(gen_date)}", ln=True, align='R')
    pdf.ln(5)
    
    # ========== ATS COMPATIBILITY SCORE ==========
    ats_score = data.get('ats_score', 0)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(page_width, 8, "ATS Compatibility Score", ln=True, align='C')
    pdf.ln(2)
    add_score_box(pdf, ats_score, page_width)
    
    # Score interpretation
    pdf.set_font("Arial", "", 10)
    if ats_score >= 80:
        interpretation = "Excellent! Your resume is well-optimized for ATS systems."
    elif ats_score >= 60:
        interpretation = "Good. Consider improving keywords and formatting."
    else:
        interpretation = "Needs improvement. Review suggestions below."
    
    pdf.cell(page_width, 6, safe_text(interpretation), ln=True, align='C')
    pdf.ln(8)
    
    # ========== CONTACT INFORMATION ==========
    add_section_header(pdf, "Contact Information", page_width)
    contact = data.get("contact_info", {})
    emails = contact.get("emails", []) or []
    phones = contact.get("phones", []) or []
    
    if emails:
        email_str = ", ".join(emails[:10])
        if len(emails) > 10:
            email_str += f" (+{len(emails) - 10} more)"
        add_key_value(pdf, "Email Addresses", email_str, page_width)
    else:
        add_key_value(pdf, "Email Addresses", "None found", page_width)
    
    if phones:
        phone_str = ", ".join(phones[:10])
        if len(phones) > 10:
            phone_str += f" (+{len(phones) - 10} more)"
        add_key_value(pdf, "Phone Numbers", phone_str, page_width)
    else:
        add_key_value(pdf, "Phone Numbers", "None found", page_width)
    
    pdf.ln(3)
    
    # ========== SKILLS ANALYSIS ==========
    add_section_header(pdf, "Skills Detected", page_width)
    skills = data.get("skills", []) or []
    if skills:
        pdf.set_font("Arial", "", 10)
        skills_text = ", ".join(skills)
        if len(skills) > 30:
            # Split into multiple lines
            skills_list = skills[:30]
            skills_text = ", ".join(skills_list) + f" (+{len(skills) - 30} more)"
        pdf.multi_cell(page_width, 6, safe_text(skills_text, 1000), align='L')
        pdf.ln(2)
        pdf.set_font("Arial", "I", 9)
        pdf.cell(page_width, 5, f"Total Skills: {len(skills)}", ln=True)
    else:
        pdf.set_font("Arial", "", 10)
        pdf.cell(page_width, 6, "No skills detected in resume.", ln=True)
    pdf.ln(5)
    
    # ========== EXPERIENCE & QUALIFICATIONS ==========
    add_section_header(pdf, "Experience & Qualifications", page_width)
    years_exp = data.get('years_experience', 0)
    add_key_value(pdf, "Years of Experience", f"{years_exp} years" if years_exp > 0 else "Not specified", page_width)
    
    mentioned_titles = data.get('mentioned_titles', []) or []
    if mentioned_titles:
        titles_str = ", ".join(mentioned_titles[:10])
        add_key_value(pdf, "Job Titles Mentioned", titles_str, page_width)
    pdf.ln(3)
    
    # ========== RESUME STATISTICS ==========
    add_section_header(pdf, "Resume Statistics", page_width)
    word_count = data.get('word_count', 0)
    char_count = data.get('character_count', 0)
    
    add_key_value(pdf, "Word Count", f"{word_count:,}", page_width)
    add_key_value(pdf, "Character Count", f"{char_count:,}", page_width)
    
    # Calculate pages (assuming ~500 words per page)
    estimated_pages = round(word_count / 500, 1) if word_count > 0 else 0
    add_key_value(pdf, "Estimated Pages", f"{estimated_pages}", page_width)
    pdf.ln(3)
    
    # ========== RESUME SECTIONS ==========
    sections = data.get('sections', {}) or {}
    if sections:
        add_section_header(pdf, "Resume Sections Detected", page_width)
        pdf.set_font("Arial", "", 10)
        
        section_names = {
            'summary': 'Summary/Objective',
            'experience': 'Experience',
            'education': 'Education',
            'skills': 'Skills Section'
        }
        
        for key, content in sections.items():
            section_name = section_names.get(key, key.title())
            if content:
                pdf.set_font("Arial", "B", 10)
                pdf.cell(page_width, 6, safe_text(section_name), ln=True)
                pdf.set_font("Arial", "", 9)
                content_preview = safe_text(content, 300)
                pdf.multi_cell(page_width, 5, content_preview, align='L')
                pdf.ln(2)
        pdf.ln(3)
    
    # ========== AI-POWERED SUGGESTIONS ==========
    suggestions = data.get('suggestions', []) or []
    if suggestions:
        add_section_header(pdf, "AI-Powered Improvement Suggestions", page_width)
        pdf.set_font("Arial", "", 10)
        
        for idx, suggestion in enumerate(suggestions[:15], 1):  # Limit to 15 suggestions
            sug_type = suggestion.get('type', 'info')
            title = suggestion.get('title', 'Suggestion')
            message = suggestion.get('message', '')
            
            # Color code by type
            if sug_type == 'error':
                pdf.set_text_color(220, 20, 60)  # Red
            elif sug_type == 'warning':
                pdf.set_text_color(255, 140, 0)  # Orange
            else:
                pdf.set_text_color(0, 100, 0)  # Green
            
            pdf.set_font("Arial", "B", 10)
            pdf.cell(page_width, 6, f"{idx}. {safe_text(title, 100)}", ln=True)
            pdf.set_font("Arial", "", 9)
            pdf.set_text_color(0, 0, 0)  # Reset to black
            if message:
                pdf.multi_cell(page_width, 5, safe_text(message, 300), align='L')
            pdf.ln(3)
        pdf.ln(2)
    
    # ========== JOB SUGGESTIONS ==========
    job_suggestions = data.get('job_suggestions', []) or []
    if job_suggestions:
        add_section_header(pdf, "Recommended Job Opportunities", page_width)
        pdf.set_font("Arial", "", 10)
        
        for idx, job in enumerate(job_suggestions[:5], 1):  # Limit to 5 jobs
            pdf.set_font("Arial", "B", 11)
            pdf.cell(page_width, 7, f"{idx}. {safe_text(job.get('title', 'Position'), 100)}", ln=True)
            pdf.set_font("Arial", "", 9)
            
            if job.get('description'):
                pdf.multi_cell(page_width, 5, safe_text(job.get('description', ''), 200), align='L')
            
            if job.get('companies'):
                companies_str = ", ".join(job.get('companies', [])[:5])
                pdf.cell(page_width, 5, f"Companies: {safe_text(companies_str)}", ln=True)
            
            if job.get('match_score'):
                pdf.cell(page_width, 5, f"Match Score: {job.get('match_score')}%", ln=True)
            
            pdf.ln(3)
        pdf.ln(2)
    
    # ========== FOOTER ==========
    pdf.ln(10)
    pdf.set_font("Arial", "I", 8)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(page_width, 5, "Generated by Smart Resume Analyzer - AI-Powered Resume Analysis", ln=True, align='C')
    pdf.cell(page_width, 5, "For best results, implement the suggestions provided above", ln=True, align='C')
    
    out = BytesIO()
    pdf.output(out)
    out.seek(0)
    return out


def format_experience(experience_text):
    """Format experience text into readable paragraphs"""
    if not experience_text:
        return ""
    # Split by double newlines to separate jobs
    jobs = experience_text.split('\n\n')
    formatted = []
    for job in jobs:
        if job.strip():
            lines = job.strip().split('\n')
            formatted.append('\n'.join(lines))
    return '\n\n'.join(formatted)

def format_education(education_text):
    """Format education text into readable paragraphs"""
    if not education_text:
        return ""
    # Split by double newlines to separate entries
    entries = education_text.split('\n\n')
    formatted = []
    for entry in entries:
        if entry.strip():
            formatted.append(entry.strip())
    return '\n'.join(formatted)

def make_modern_minimalist_pdf(data):
    """Create Modern Minimalist template PDF with complete details"""
    pdf = FPDF()
    pdf.add_page()
    page_width = 190
    margin = 10
    
    # Header with gradient effect (simulated with colored bar)
    pdf.set_fill_color(102, 126, 234)  # Purple-blue
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 24)
    pdf.set_xy(margin, margin)
    
    # Accent bar
    pdf.set_fill_color(251, 191, 36)  # Gold accent
    pdf.rect(margin, margin, 4, 35, 'F')
    
    # Name and title
    pdf.set_fill_color(102, 126, 234)
    pdf.set_xy(margin + 8, margin + 8)
    name = safe_text(data.get('name', 'Your Name'), 50)
    pdf.cell(page_width - 20, 12, name.upper(), ln=True)
    pdf.set_font("Arial", "", 12)
    title = safe_text(data.get('title', 'Professional Title'), 50)
    pdf.set_xy(margin + 8, pdf.get_y())
    pdf.cell(page_width - 20, 8, title, ln=True)
    
    # Contact Information
    pdf.set_font("Arial", "", 9)
    contact_info = []
    if data.get('email'):
        contact_info.append(safe_text(data.get('email', ''), 50))
    if data.get('phone'):
        contact_info.append(safe_text(data.get('phone', ''), 30))
    if data.get('location'):
        contact_info.append(safe_text(data.get('location', ''), 40))
    
    if contact_info:
        pdf.set_xy(margin + 8, pdf.get_y() + 2)
        pdf.cell(page_width - 20, 6, ' | '.join(contact_info), ln=True)
    
    pdf.ln(12)
    
    # Content sections
    pdf.set_text_color(0, 0, 0)
    
    # Professional Summary
    if data.get('summary'):
        pdf.set_font("Arial", "B", 14)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(page_width, 8, " PROFESSIONAL SUMMARY ", ln=True, fill=True)
        pdf.set_font("Arial", "", 10)
        pdf.ln(3)
        summary = safe_text(data.get('summary', ''), 800)
        pdf.multi_cell(page_width, 6, summary, align='L')
        pdf.ln(8)
    
    # Professional Experience
    if data.get('experience'):
        pdf.set_font("Arial", "B", 14)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(page_width, 8, " PROFESSIONAL EXPERIENCE ", ln=True, fill=True)
        pdf.set_font("Arial", "", 10)
        pdf.ln(3)
        experience = format_experience(data.get('experience', ''))
        pdf.multi_cell(page_width, 6, safe_text(experience, 1500), align='L')
        pdf.ln(8)
    
    # Education
    if data.get('education'):
        pdf.set_font("Arial", "B", 14)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(page_width, 8, " EDUCATION ", ln=True, fill=True)
        pdf.set_font("Arial", "", 10)
        pdf.ln(3)
        education = format_education(data.get('education', ''))
        pdf.multi_cell(page_width, 6, safe_text(education, 800), align='L')
        pdf.ln(8)
    
    # Skills
    if data.get('skills'):
        pdf.set_font("Arial", "B", 14)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(page_width, 8, " SKILLS ", ln=True, fill=True)
        pdf.set_font("Arial", "", 10)
        pdf.ln(3)
        skills = safe_text(data.get('skills', ''), 500)
        # Format skills with dashes (bullet character not supported by default font)
        skills_list = [s.strip() for s in skills.split(',') if s.strip()]
        if skills_list:
            for skill in skills_list[:15]:  # Limit to 15 skills
                pdf.cell(page_width, 6, f"- {skill}", ln=True)
        else:
            pdf.multi_cell(page_width, 6, skills, align='L')
        pdf.ln(5)
    
    # Links/Additional Information
    if data.get('links'):
        pdf.set_font("Arial", "B", 14)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(page_width, 8, " LINKS & PORTFOLIO ", ln=True, fill=True)
        pdf.set_font("Arial", "", 10)
        pdf.ln(3)
        links = [l.strip() for l in safe_text(data.get('links', ''), 300).split(',') if l.strip()]
        for link in links[:5]:  # Limit to 5 links
            pdf.cell(page_width, 6, f"- {link}", ln=True)
    
    out = BytesIO()
    pdf.output(out)
    out.seek(0)
    return out

def make_professional_classic_pdf(data):
    """Create Professional Classic template PDF with sidebar and complete details"""
    pdf = FPDF()
    pdf.add_page()
    page_width = 190
    sidebar_width = 65
    main_width = page_width - sidebar_width - 5
    margin = 10
    
    # Sidebar
    pdf.set_fill_color(45, 55, 72)  # Dark gray
    pdf.rect(margin, margin, sidebar_width, 280, 'F')
    
    # Sidebar content
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 18)
    pdf.set_xy(margin + 3, margin + 15)
    name = safe_text(data.get('name', 'Your Name'), 30)
    pdf.multi_cell(sidebar_width - 6, 8, name.upper(), align='C')
    
    # Contact Information in sidebar
    pdf.set_font("Arial", "", 9)
    y_pos = pdf.get_y() + 8
    if data.get('email'):
        pdf.set_xy(margin + 3, y_pos)
        pdf.multi_cell(sidebar_width - 6, 4, safe_text(data.get('email', ''), 40), align='C')
        y_pos = pdf.get_y() + 2
    if data.get('phone'):
        pdf.set_xy(margin + 3, y_pos)
        pdf.multi_cell(sidebar_width - 6, 4, safe_text(data.get('phone', ''), 30), align='C')
        y_pos = pdf.get_y() + 2
    if data.get('location'):
        pdf.set_xy(margin + 3, y_pos)
        pdf.multi_cell(sidebar_width - 6, 4, safe_text(data.get('location', ''), 30), align='C')
        y_pos = pdf.get_y() + 8
    
    # Skills in sidebar
    if data.get('skills'):
        pdf.set_xy(margin + 3, y_pos)
        pdf.set_font("Arial", "B", 11)
        pdf.multi_cell(sidebar_width - 6, 5, "SKILLS", align='C')
        pdf.set_font("Arial", "", 8)
        pdf.set_xy(margin + 3, pdf.get_y() + 2)
        skills = safe_text(data.get('skills', ''), 300)
        skills_list = [s.strip() for s in skills.split(',') if s.strip()]
        for skill in skills_list[:12]:  # Limit for sidebar
            pdf.set_xy(margin + 3, pdf.get_y() + 1)
            pdf.multi_cell(sidebar_width - 6, 4, f"- {skill}", align='L')
    
    # Links in sidebar
    if data.get('links'):
        pdf.set_xy(margin + 3, pdf.get_y() + 5)
        pdf.set_font("Arial", "B", 11)
        pdf.multi_cell(sidebar_width - 6, 5, "LINKS", align='C')
        pdf.set_font("Arial", "", 7)
        links = [l.strip() for l in safe_text(data.get('links', ''), 200).split(',') if l.strip()]
        for link in links[:4]:  # Limit for sidebar
            pdf.set_xy(margin + 3, pdf.get_y() + 1)
            pdf.multi_cell(sidebar_width - 6, 3, link, align='C')
    
    # Main content area
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 22)
    pdf.set_xy(margin + sidebar_width + 5, margin + 5)
    pdf.set_fill_color(102, 126, 234)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(main_width, 10, name.upper(), ln=True, fill=True)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "", 13)
    pdf.set_xy(margin + sidebar_width + 5, pdf.get_y() + 2)
    title = safe_text(data.get('title', 'Professional Title'), 50)
    pdf.cell(main_width, 8, title, ln=True)
    pdf.ln(8)
    
    # Professional Summary
    if data.get('summary'):
        pdf.set_font("Arial", "B", 13)
        pdf.set_xy(margin + sidebar_width + 5, pdf.get_y())
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(main_width, 7, " PROFESSIONAL SUMMARY ", ln=True, fill=True)
        pdf.set_font("Arial", "", 10)
        pdf.set_xy(margin + sidebar_width + 5, pdf.get_y() + 2)
        summary = safe_text(data.get('summary', ''), 800)
        pdf.multi_cell(main_width, 5, summary, align='L')
        pdf.ln(5)
    
    # Professional Experience
    if data.get('experience'):
        pdf.set_font("Arial", "B", 13)
        pdf.set_xy(margin + sidebar_width + 5, pdf.get_y())
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(main_width, 7, " PROFESSIONAL EXPERIENCE ", ln=True, fill=True)
        pdf.set_font("Arial", "", 10)
        pdf.set_xy(margin + sidebar_width + 5, pdf.get_y() + 2)
        experience = format_experience(data.get('experience', ''))
        pdf.multi_cell(main_width, 5, safe_text(experience, 1500), align='L')
        pdf.ln(5)
    
    # Education
    if data.get('education'):
        pdf.set_font("Arial", "B", 13)
        pdf.set_xy(margin + sidebar_width + 5, pdf.get_y())
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(main_width, 7, " EDUCATION ", ln=True, fill=True)
        pdf.set_font("Arial", "", 10)
        pdf.set_xy(margin + sidebar_width + 5, pdf.get_y() + 2)
        education = format_education(data.get('education', ''))
        pdf.multi_cell(main_width, 5, safe_text(education, 800), align='L')
    
    out = BytesIO()
    pdf.output(out)
    out.seek(0)
    return out

def make_creative_bold_pdf(data):
    """Create Creative Bold template PDF with complete details"""
    pdf = FPDF()
    pdf.add_page()
    page_width = 190
    margin = 10
    
    # Bold header with color block
    pdf.set_fill_color(245, 87, 108)  # Pink-red gradient color
    pdf.rect(margin, margin, page_width, 30, 'F')
    
    # Name in bold
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 28)
    pdf.set_xy(margin + 5, margin + 6)
    name = safe_text(data.get('name', 'Your Name'), 40)
    pdf.cell(page_width - 10, 12, name.upper(), ln=True)
    
    # Title with accent color
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 14)
    pdf.set_xy(margin + 5, pdf.get_y())
    title = safe_text(data.get('title', 'Professional Title'), 50)
    pdf.cell(page_width - 10, 8, title.upper(), ln=True)
    pdf.ln(12)
    
    # Contact info in a styled box
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "", 9)
    contact_info = []
    if data.get('email'):
        contact_info.append(f"Email: {safe_text(data.get('email', ''), 40)}")
    if data.get('phone'):
        contact_info.append(f"Phone: {safe_text(data.get('phone', ''), 30)}")
    if data.get('location'):
        contact_info.append(f"Location: {safe_text(data.get('location', ''), 30)}")
    
    if contact_info:
        pdf.set_fill_color(250, 250, 250)
        pdf.rect(margin, pdf.get_y(), page_width, 12, 'F')
        pdf.set_xy(margin + 5, pdf.get_y() + 3)
        pdf.cell(page_width - 10, 6, ' | '.join(contact_info), ln=True)
        pdf.ln(8)
    
    # Sections with bold headers
    pdf.set_text_color(0, 0, 0)
    
    # Professional Summary
    if data.get('summary'):
        pdf.set_font("Arial", "B", 16)
        pdf.set_fill_color(245, 87, 108)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(page_width, 8, " PROFESSIONAL SUMMARY ", ln=True, fill=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "", 10)
        pdf.ln(4)
        summary = safe_text(data.get('summary', ''), 800)
        pdf.multi_cell(page_width, 6, summary, align='L')
        pdf.ln(6)
    
    # Professional Experience
    if data.get('experience'):
        pdf.set_font("Arial", "B", 16)
        pdf.set_fill_color(245, 87, 108)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(page_width, 8, " PROFESSIONAL EXPERIENCE ", ln=True, fill=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "", 10)
        pdf.ln(4)
        experience = format_experience(data.get('experience', ''))
        pdf.multi_cell(page_width, 6, safe_text(experience, 1500), align='L')
        pdf.ln(6)
    
    # Education
    if data.get('education'):
        pdf.set_font("Arial", "B", 16)
        pdf.set_fill_color(245, 87, 108)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(page_width, 8, " EDUCATION ", ln=True, fill=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "", 10)
        pdf.ln(4)
        education = format_education(data.get('education', ''))
        pdf.multi_cell(page_width, 6, safe_text(education, 800), align='L')
        pdf.ln(6)
    
    # Skills
    if data.get('skills'):
        pdf.set_font("Arial", "B", 16)
        pdf.set_fill_color(245, 87, 108)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(page_width, 8, " SKILLS ", ln=True, fill=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "", 10)
        pdf.ln(4)
        skills = safe_text(data.get('skills', ''), 500)
        skills_list = [s.strip() for s in skills.split(',') if s.strip()]
        if skills_list:
            for skill in skills_list[:15]:  # Limit to 15 skills
                pdf.cell(page_width, 6, f"- {skill}", ln=True)
        else:
            pdf.multi_cell(page_width, 6, skills, align='L')
        pdf.ln(4)
    
    # Links & Portfolio
    if data.get('links'):
        pdf.set_font("Arial", "B", 16)
        pdf.set_fill_color(245, 87, 108)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(page_width, 8, " LINKS & PORTFOLIO ", ln=True, fill=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "", 10)
        pdf.ln(4)
        links = [l.strip() for l in safe_text(data.get('links', ''), 300).split(',') if l.strip()]
        for link in links[:5]:  # Limit to 5 links
            pdf.cell(page_width, 6, f"- {link}", ln=True)
    
    out = BytesIO()
    pdf.output(out)
    out.seek(0)
    return out

@app.route("/api/templates/generate", methods=["POST"])
def api_templates_generate():
    try:
        # Build a generated resume from form data
        form = request.form
        template_id = form.get("template_id", "modern_minimalist")
        
        # Extract form data
        full_name = form.get("full_name", "Your Name")
        # Try to extract title from experience if not provided
        experience_text = form.get("experience", "")
        title = form.get("title", "")
        if not title and experience_text:
            # Try to extract job title from first line of experience
            first_line = experience_text.split('\n')[0] if experience_text else ""
            if " at " in first_line.lower():
                title = first_line.split(" at ")[0].strip()
            elif first_line:
                title = first_line.split('\n')[0].strip()[:50]
        
        data = {
            "name": full_name,
            "title": title or "Professional",
            "email": form.get("email", ""),
            "phone": form.get("phone", ""),
            "location": form.get("location", ""),
            "summary": form.get("summary", ""),
            "skills": form.get("skills", ""),
            "experience": experience_text,
            "education": form.get("education", ""),
            "links": form.get("links", "")
        }
        
        # Generate PDF based on template
        if template_id == "modern_minimalist":
            pdf_io = make_modern_minimalist_pdf(data)
            filename = "resume_modern_minimalist.pdf"
        elif template_id == "professional_classic":
            pdf_io = make_professional_classic_pdf(data)
            filename = "resume_professional_classic.pdf"
        elif template_id == "creative_bold":
            pdf_io = make_creative_bold_pdf(data)
            filename = "resume_creative_bold.pdf"
        else:
            # Default to modern minimalist
            pdf_io = make_modern_minimalist_pdf(data)
            filename = "resume_modern_minimalist.pdf"
        
        return send_file(pdf_io, mimetype="application/pdf", as_attachment=True, download_name=filename)
    except Exception as e:
        return jsonify({"error": f"Failed to generate resume: {str(e)}"}), 500


@app.route("/api/download", methods=["POST"])
def api_download():
    try:
        # Accept JSON analysis result & produce detailed PDF report
        data = request.get_json() or {}
        title = "Resume Analysis Report"
        
        # Ensure we have a generated_at field
        if 'generated_at' not in data or not data.get('generated_at'):
            data['generated_at'] = datetime.datetime.utcnow().isoformat() + "Z"
        
        # Generate the detailed PDF report
        pdf_io = make_pdf_bytes(title, data)
        return send_file(pdf_io, mimetype="application/pdf", as_attachment=True, download_name="resume_analysis_report.pdf")
    except Exception as e:
        # Return JSON error instead of letting Flask return HTML error page
        import traceback
        error_details = str(e)
        return jsonify({"error": f"Failed to generate PDF: {error_details}"}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
# ...existing code...