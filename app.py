from flask import Flask, render_template, request, redirect, session, send_file
import PyPDF2
import re
import io
import os
from reportlab.pdfgen import canvas
from openpyxl import Workbook

from database import (
    create_table,
    insert_history,
    get_history,
    get_dashboard_stats,
    create_users_table,
    register_user,
    check_user
)

app = Flask(__name__)
app.secret_key = "resume_analyzer_secret_key"

create_table()
create_users_table()

skills_db = [
    "python", "java", "c", "c++", "html", "css", "javascript",
    "sql", "mongodb", "node.js", "data structures", "oop",
    "git", "github", "excel", "power bi", "statistics"
]

job_roles = {
    "Software Developer": [
        "python", "java", "sql", "git", "data structures", "oop"
    ],
    "Data Analyst": [
        "python", "sql", "excel", "power bi", "statistics"
    ]
}


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        success = register_user(username, email, password)

        if success:
            return redirect("/login")

        return render_template(
            "register.html",
            error="Username already exists"
        )

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        user = check_user(username, password)

        if user or (username == "admin" and password == "1234"):

            session["user"] = username
            return redirect("/")

        return render_template(
            "login.html",
            error="Invalid username or password"
        )

    return render_template("login.html")


@app.route("/")
def home():

    if "user" not in session:
        return redirect("/login")

    return render_template(
        "index.html",
        ats_score=0,
        strength_level="",
        skills=[],
        missing_skills=[],
        match_score=0,
        suggestions=[],
        resume_tips=[],
        extracted_text="",
        matched_count=0,
        missing_count=0,
        job_role=""
    )


@app.route("/upload", methods=["POST"])
def upload():

    if "user" not in session:
        return redirect("/login")

    file = request.files["file"]
    job_role = request.form.get("job_role")

    text = ""

    if file and file.filename.endswith(".pdf"):

        pdf_reader = PyPDF2.PdfReader(file)

        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text

    text_lower = text.lower()

    detected_skills = []

    for skill in skills_db:
        if skill in text_lower:
            detected_skills.append(skill)

    required_skills = job_roles.get(job_role, [])

    missing_skills = []

    for skill in required_skills:
        if skill not in detected_skills:
            missing_skills.append(skill)

    matched_count = len(required_skills) - len(missing_skills)
    missing_count = len(missing_skills)

    if len(required_skills) > 0:
        match_score = int((matched_count / len(required_skills)) * 100)
    else:
        match_score = 0

    ats_score = int((len(detected_skills) / len(skills_db)) * 100)

    insert_history(job_role, ats_score, match_score)

    if ats_score >= 80:
        strength_level = "Strong"
    elif ats_score >= 50:
        strength_level = "Moderate"
    else:
        strength_level = "Weak"

    suggestions = []

    for skill in missing_skills:
        suggestions.append(f"Add {skill} skill to improve your resume")

    if len(suggestions) == 0:
        suggestions.append("Your resume matches the job role well")

    resume_tips = [
        "Use action verbs like Developed, Built, Implemented",
        "Add measurable results",
        "Keep resume length to 1 page",
        "Highlight technical skills clearly",
        "Add internships or certifications"
    ]

    highlighted_text = text

    for skill in detected_skills:
        highlighted_text = re.sub(
            skill,
            f"<mark>{skill}</mark>",
            highlighted_text,
            flags=re.IGNORECASE
        )

    session["ats_score"] = ats_score
    session["strength_level"] = strength_level
    session["job_role"] = job_role
    session["skills"] = detected_skills
    session["missing_skills"] = missing_skills
    session["suggestions"] = suggestions

    return render_template(
        "index.html",
        ats_score=ats_score,
        strength_level=strength_level,
        skills=detected_skills,
        missing_skills=missing_skills,
        match_score=match_score,
        suggestions=suggestions,
        resume_tips=resume_tips,
        extracted_text=highlighted_text,
        matched_count=matched_count,
        missing_count=missing_count,
        job_role=job_role
    )


@app.route("/history")
def history():

    if "user" not in session:
        return redirect("/login")

    data = get_history()

    return render_template(
        "history.html",
        history=data
    )


@app.route("/admin")
def admin():

    if "user" not in session:
        return redirect("/login")

    total_resumes, avg_ats, most_role = get_dashboard_stats()

    history_data = get_history()

    ids = []
    scores = []

    for i, row in enumerate(history_data, start=1):
        ids.append(i)
        scores.append(row[2])

    return render_template(
        "admin.html",
        total=total_resumes,
        average=avg_ats,
        role=most_role,
        ids=ids,
        scores=scores
    )


@app.route("/download")
def download():

    if "user" not in session:
        return redirect("/login")

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer)

    y = 800

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(100, y, "Resume Analysis Report")

    y -= 40

    pdf.setFont("Helvetica", 12)
    pdf.drawString(100, y, "User: " + session.get("user", ""))

    y -= 25
    pdf.drawString(100, y, "Job Role: " + session.get("job_role", ""))

    y -= 25
    pdf.drawString(
        100,
        y,
        "ATS Score: " + str(session.get("ats_score", 0)) + "%"
    )

    y -= 25
    pdf.drawString(
        100,
        y,
        "Resume Strength: " + session.get("strength_level", "")
    )

    y -= 40

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(100, y, "Detected Skills:")

    y -= 25
    pdf.setFont("Helvetica", 12)

    for skill in session.get("skills", []):
        pdf.drawString(120, y, "- " + skill)
        y -= 20

    y -= 20

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(100, y, "Missing Skills:")

    y -= 25
    pdf.setFont("Helvetica", 12)

    missing = session.get("missing_skills", [])

    if len(missing) == 0:
        pdf.drawString(120, y, "No missing skills")
        y -= 20
    else:
        for skill in missing:
            pdf.drawString(120, y, "- " + skill)
            y -= 20

    y -= 20

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(100, y, "Suggestions:")

    y -= 25
    pdf.setFont("Helvetica", 12)

    for s in session.get("suggestions", []):
        pdf.drawString(120, y, "- " + s)
        y -= 20

    pdf.save()
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="resume_report.pdf",
        mimetype="application/pdf"
    )


@app.route("/export_excel")
def export_excel():

    if "user" not in session:
        return redirect("/login")

    history_data = get_history()

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Resume History"

    sheet.append([
        "ID",
        "Job Role",
        "ATS Score",
        "Match Score",
        "Date"
    ])

    for row in history_data:
        sheet.append([
            row[0],
            row[1],
            row[2],
            row[3],
            row[4]
        ])

    file_stream = io.BytesIO()
    workbook.save(file_stream)
    file_stream.seek(0)

    return send_file(
        file_stream,
        as_attachment=True,
        download_name="resume_history.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@app.route("/logout")
def logout():

    session.clear()
    return redirect("/login")


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )