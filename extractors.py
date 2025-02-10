import re
import pdfplumber
import docx
import spacy

# Predefined Skills, Job Roles, and Domains
SKILLS_LIST = {"Python", "Java", "Machine Learning", "Deep Learning", "Data Science", "SQL", "JavaScript",
               "AWS", "React", "TensorFlow", "Web Scraping", "Google PaLM API", "LangChain", "EDA","C","C++","HTML","CSS","PHP","Node.js","Angular",
               "Vue.js","Django","Flask","Laravel","SpringBoot","Hibernate","JPA","JSP","Servlets","JDBC","JSTL","Thymeleaf","Junit","Mockito","PowerMock",
               "TestNG","Selenium","Docker","Kubernetes","JIRA","Confluence","Git","Bitbucket","Jenkins","TypeScript", "Go", "Ruby", "Rust", "Scala","Bootstrap","MySQL", "PostgreSQL", "MongoDB", "SQLite", "Firebase", "Oracle", "Cassandra"
               "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "Terraform", "Jenkins", "CI/CD","Machine Learning", "Deep Learning", "Natural Language Processing", "Computer Vision", 
    "TensorFlow", "PyTorch", "Scikit-learn", "Keras", "Hugging Face", "LangChain", "Google PaLM API","Data Analysis", "Data Visualization", "Pandas", "NumPy", "Matplotlib", "Seaborn", "EDA", 
    "Big Data", "Hadoop", "Spark", "Tableau", "Power BI", "Google Analytics", "Ethical Hacking", "Penetration Testing", "Network Security", "Cryptography", "SIEM", 
    "Security Audits", "OWASP", "SOC Analyst","Linux", "Windows Server", "Networking", "TCP/IP", "Bash Scripting", "Cloud Computing","Project Management", "Problem-Solving", "Communication Skills", "Teamwork", "Leadership", 
    "Time Management", "Critical Thinking""Git", "GitHub", "Agile", "Scrum", "JIRA", "Trello", "Microservices", "REST API", 
    "GraphQL", "Unit Testing", "CI/CD", "Test Automation"}

JOB_ROLES = {"Software Engineer", "Data Scientist", "Machine Learning Engineer", "Project Manager",
             "AI Researcher", "Data Analyst", "Backend Developer", "Frontend Developer"}

DOMAINS = {"Healthcare", "Finance", "E-commerce", "Education", "Cybersecurity", "Robotics", "Blockchain"}

# Extract text from PDF
def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

# Extract text from DOCX
def extract_text_from_docx(docx_path):
    doc = docx.Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs])

# Extract Name using NLP
import re
import spacy

# Load the spaCy model for Name Entity Recognition (NER)
nlp = spacy.load("en_core_web_sm")

def extract_name(text):
    # Get the first non-empty line
    lines = text.split("\n")
    first_non_empty_line = next((line.strip() for line in lines if line.strip()), "")

    #print("\n=== Debugging: Extracted Resume Text (First Line) ===\n")
    #print(first_non_empty_line)  # Debugging output

    # Basic heuristic check for a name
    if 2 <= len(first_non_empty_line.split()) <= 4 and re.match(r'^[A-Za-z\s]+$', first_non_empty_line):
        #print(f"✅ First Line Looks Like a Name: {first_non_empty_line}")
        return first_non_empty_line

    #print("❌ First Line Does Not Look Like a Name, Using NLP Model...")

    # Use spaCy's Named Entity Recognition (NER) as fallback
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":  # Look for a "PERSON" entity
            #print(f"✅ NER Detected Name: {ent.text}")
            return ent.text

    #print("❌ Name Not Found by NER")
    return "Not Found"


# Extract Email
def extract_email(text):
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match = re.search(email_pattern, text)
    return match.group(0) if match else "Not Found"

# Extract Phone Number
def extract_phone(text):
    phone_pattern = r'\b(?:\+?\d{1,3})?\s?(?:\(?\d{3}\)?[\s.-]?)?\d{3}[\s.-]?\d{4}\b'
    match = re.search(phone_pattern, text)
    return match.group(0) if match else "Not Found"

# Extract Skills
def extract_skills(text):
    found_skills = {skill for skill in SKILLS_LIST if skill.lower() in text.lower()}
    return ", ".join(sorted(found_skills)) if found_skills else "Not Found"


def extract_experience(text):
    exp_pattern = r'(?i)(\d+)\s*(?:\+?\s*years?|months?)\s*(?:of experience|experience|working)?'
    match = re.search(exp_pattern, text)
    return f"{match.group(1)} years" if match else "0 years"

# Extract Job Role
def extract_job_role(text):
    found_roles = {role for role in JOB_ROLES if role.lower() in text.lower()}
    return ", ".join(sorted(found_roles)) if found_roles else "Not Specific"

# Extract Domain
def extract_domain(text):
    found_domains = {domain for domain in DOMAINS if domain.lower() in text.lower()}
    return ", ".join(sorted(found_domains)) if found_domains else "Not Found"


