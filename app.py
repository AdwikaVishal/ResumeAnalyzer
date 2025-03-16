from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from PyPDF2 import PdfReader
from docx import Document
from textblob import TextBlob
import os
import nltk

nltk.download('punkt')

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

SKILLS = {
    "Tech": ["Python", "Java", "C++", "SQL", "Machine Learning", "JavaScript", "HTML", "CSS", "Cloud Computing", "Data Science", "DevOps", "Cybersecurity", "AI/Deep Learning", "Blockchain", "Database Management", "App Development"],
    "Pharma": ["Clinical Trials", "Drug Research", "Pharmaceuticals", "Biotechnology", "Dermatology", "Pharmacology", "Regulatory Affairs", "Bioinformatics", "Drug Development", "Pharmaceutical Marketing", "Pharmacovigilance", "Genomics", "Toxicology"],
    "Healthcare": ["Patient Care", "Medical Research", "Public Health", "Healthcare Management", "Nursing", "Health Informatics", "Telemedicine", "Epidemiology", "Mental Health", "Medical Coding", "Health Policy", "Healthcare Analytics"],
    "Education": ["Teaching", "Curriculum Development", "EdTech", "Instructional Design", "Classroom Management", "Student Assessment", "E-learning", "Academic Counseling", "Learning Analytics", "Professional Development", "Education Technology Integration", "Adult Education"],
    "Banking": ["Financial Analysis", "Investment Banking", "Risk Management", "Corporate Banking", "Retail Banking", "Mortgage Lending", "Credit Analysis", "Fraud Prevention", "Financial Modelling", "Banking Regulations", "Wealth Management", "Accounting", "Compliance", "Financial Reporting", "Trade Finance"]
}


def extract_text(file_path):
    """Extract text from PDF or DOCX file"""
    text = ""
    if file_path.endswith('.pdf'):
        reader = PdfReader(file_path)
        for page in reader.pages:
            text += page.extract_text() or ""
    elif file_path.endswith('.docx'):
        doc = Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    return text

def extract_skills(text, category):
    """Extract relevant skills based on category"""
    extracted_skills = [skill for skill in SKILLS[category] if skill.lower() in text.lower()]
    return extracted_skills

def extract_experience(text):
    """Extract experience-related sentences"""
    return [sentence.strip() for sentence in text.split("\n") if "experience" in sentence.lower()]

def extract_education(text):
    """Extract education-related sentences"""
    keywords = ["Bachelor", "Master", "PhD", "University", "Degree",]
    return [sentence.strip() for sentence in text.split("\n") if any(keyword in sentence for keyword in keywords)]

def analyze_sentiment(text):
    """Analyze sentiment of the text"""
    polarity = TextBlob(text).sentiment.polarity
    return "Positive" if polarity > 0.1 else "Negative" if polarity < -0.1 else "Neutral"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        category = request.form.get('category')
        if category not in SKILLS:
            return "Invalid category", 400
        return redirect(url_for('upload_resume', category=category))

    return render_template('upload.html')

@app.route('/upload/<category>', methods=['GET', 'POST'])
def upload_resume(category):
    if request.method == 'POST':
        file = request.files.get('resume')
        if not file or file.filename == '':
            return "No file uploaded", 400

        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        return redirect(url_for('result', category=category, filename=file.filename))

    return render_template(f'upload_{category}.html', category=category)

@app.route('/result/<category>/<filename>')
def result(category, filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    text = extract_text(file_path)

    skills = extract_skills(text, category)
    experience = extract_experience(text)
    education = extract_education(text)

    sentiment = analyze_sentiment(text)

    score = min(100, len(skills) * 10 + len(experience) * 5 + len(education) * 5)

    analysis = {
        'skills': skills,
        'experience': experience,
        'education': education,
        'sentiment': sentiment,
        'score': score
    }

    return render_template(f'result_{category}.html', filename=filename, analysis=analysis)

@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
