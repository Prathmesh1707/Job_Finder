from flask import Flask, request, jsonify
import os
import pdfplumber
import spacy
import json
import re

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'backend/uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

PARSED_DATA_FOLDER = os.path.join(os.getcwd(), 'backend/parsed_data')
os.makedirs(PARSED_DATA_FOLDER, exist_ok=True)

# Load Spacy NLP model
nlp = spacy.load('en_core_web_sm')

# Function to extract skills from resume text dynamically
def extract_skills(text):
    """Extract skills dynamically from resume text using pattern matching."""
    # List of possible skills or technology-related words to look for
    skill_keywords = [
        "Python", "Java", "C++", "SQL", "JavaScript", "HTML", "CSS", "PHP", 
        "Ruby", "Swift", "Git", "Linux", "Machine Learning", "Data Science", 
        "Deep Learning", "Artificial Intelligence", "MySQL", "PostgreSQL", 
        "MongoDB", "Docker", "AWS", "TensorFlow", "Keras", "Flutter", "React"
    ]
    
    skills = []
    for keyword in skill_keywords:
        if keyword.lower() in text.lower():
            skills.append(keyword)
    return skills

# Function to parse personal details
def extract_personal_details(text):
    """Extract personal details dynamically from the resume text."""
    name_match = re.search(r"([A-Za-z]+ [A-Za-z]+)", text)
    phone_match = re.search(r"(\+?\d{1,2}[-\s]?)?\(?\d{3,4}\)?[-\s]?\d{3}[-\s]?\d{3,4}", text)
    email_match = re.search(r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", text)

    personal_details = {
        "name": name_match.group(0) if name_match else "Unknown",
        "phone": phone_match.group(0) if phone_match else "Not Found",
        "email": email_match.group(0) if email_match else "Not Found"
    }

    return personal_details

# Function to extract education details dynamically
def extract_education(text):
    """Extract education details dynamically from resume text."""
    education = []
    edu_pattern = r"(\b(?:B\.?Tech|M\.?Tech|B\.?Com|M\.?Com|M\.?C\.?A\.?|B\.?A\.?|Diploma)\b.*?(\d{4}\s?[-]?\s?\d{4}|[0-9]+))"
    matches = re.findall(edu_pattern, text)

    for match in matches:
        education.append({
            "degree": match[0],
            "duration": match[1]
        })
    return education

# Function to extract projects dynamically
def extract_projects(text):
    """Extract project details dynamically from the resume text."""
    projects = []
    project_pattern = r"(\b[A-Za-z0-9\s]+[A-Za-z0-9]+)\s*\d{1,2}\s*[A-Za-z]+\,\s*\d{1,2}\s*[A-Za-z]+"
    matches = re.findall(project_pattern, text)
    
    for match in matches:
        projects.append({
            "project_name": match,
            "skills": extract_skills(text)
        })
    return projects

# Resume Parsing Function
def extract_resume_details(pdf_path):
    """Extracts text and skills from the uploaded resume dynamically."""
    with pdfplumber.open(pdf_path) as pdf:
        text = ''.join([page.extract_text() for page in pdf.pages])

    skills = extract_skills(text)
    personal_details = extract_personal_details(text)
    education = extract_education(text)
    projects = extract_projects(text)

    return {
        "skills": skills,
        "personal_details": personal_details,
        "education": education,
        "projects": projects,
        "text": text  # This is the raw text, if needed
    }

# Flask Route to handle the file upload
@app.route('/upload', methods=['POST'])
def upload_resume():
    """Handle file upload, extract details, and save to JSON dynamically."""
    if 'resume' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['resume']
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    try:
        # Parse the resume details dynamically
        resume_details = extract_resume_details(file_path)

        # Save the parsed details as a JSON file
        json_file_path = os.path.join(PARSED_DATA_FOLDER, file.filename.replace('.pdf', '.json'))
        with open(json_file_path, 'w') as json_file:
            json.dump(resume_details, json_file, indent=4)

        return jsonify({"message": "Resume uploaded and parsed successfully", "file": json_file_path}), 200

    except Exception as e:
        return jsonify({"error": "Failed to parse resume", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
