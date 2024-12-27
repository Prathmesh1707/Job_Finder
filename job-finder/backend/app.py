from flask import Flask, request, jsonify, render_template
import os
import pdfplumber
import spacy
import requests
from bs4 import BeautifulSoup
  # For handling CORS issues

app = Flask(__name__)

# Enable CORS for all routes


UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load SpaCy's pre-trained NER model
nlp = spacy.load('en_core_web_sm')

# Extended skill list (Add or modify skills as needed)
extended_skills = [
    "Python", "Java", "C++", "SQL", "HTML", "CSS", "JavaScript", "Node.js", 
    "React", "Angular", "Vue.js", "PHP", "Ruby", "Go", "Swift", "Kotlin", 
    "MySQL", "MongoDB", "PostgreSQL", "Git", "Docker", "AWS", "Azure", 
    "Machine Learning", "Data Science", "TensorFlow", "PyTorch", "Jupyter", 
    "Tableau", "Power BI", "R", "Scala", "Hadoop", "Spark", "Linux", "Bash", 
    "DevOps", "GitHub", "REST APIs", "GraphQL", "Nginx", "Bootstrap", "Sass", 
    "jQuery", "Firebase", "Cloud Computing", "IoT", "UI/UX", "Flutter", "Django", 
    "Flask", "ASP.NET", "C#", "Android", "iOS", "Deep Learning", "Big Data", 
    "Kubernetes", "Salesforce", "Shopify", "ElasticSearch", "Vagrant", "Kotlin", 
    "Flutter", "Xamarin", "CouchDB", "TensorFlow", "Hadoop"
]

# Function to extract details from the resume
def extract_resume_details(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ''.join([page.extract_text() for page in pdf.pages])
    
    doc = nlp(text)  # NLP model to analyze the text
    
    # Extract skills from named entities recognized by spaCy's NER model
    ner_skills = [ent.text for ent in doc.ents if ent.label_ in ['SKILL', 'TECHNOLOGY', 'SOFTSKILL']]
    
    # Add predefined skills from the extended list
    found_skills = set(ner_skills)
    
    # Case-insensitive search for skills from the extended list
    for skill in extended_skills:
        if skill.lower() in text.lower():
            found_skills.add(skill)
    
    return {
        "skills": list(found_skills),
        "text": text
    }

# Function to search for jobs based on skills
def search_jobs(skills, location=""):
    query = '+'.join(skills)
    url = f"https://www.indeed.com/jobs?q={query}&l={location}"
    response = requests.get(url)

    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    jobs = []
    for job_card in soup.find_all('div', class_='job_seen_beacon'):
        title = job_card.find('h2').text.strip() if job_card.find('h2') else 'N/A'
        company = job_card.find('span', class_='companyName').text.strip() if job_card.find('span', 'companyName') else 'N/A'
        link = "https://www.indeed.com" + job_card.find('a')['href'] if job_card.find('a') else 'N/A'
        jobs.append({"title": title, "company": company, "link": link})

    return jobs

# Route for the homepage
@app.route('/')
def index():
    return render_template('index.html')

# Route for handling resume upload and processing
@app.route('/upload', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['resume']
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    print(f"File saved at: {file_path}")  # Debugging log
    
    try:
        resume_details = extract_resume_details(file_path)
        print("Resume details extracted successfully")  # Debugging log
    except Exception as e:
        return jsonify({"error": "Failed to parse resume", "details": str(e)}), 500

    skills = resume_details.get("skills", [])
    if not skills:
        return jsonify({"error": "No skills found in resume"}), 400

    try:
        jobs = search_jobs(skills)
        print(f"Jobs found: {jobs}")  # Debugging log
    except Exception as e:
        return jsonify({"error": "Failed to search jobs", "details": str(e)}), 500

    return jsonify({"resume_details": resume_details, "jobs": jobs})

if __name__ == '__main__':
    app.run(debug=True)
