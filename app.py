from flask import Flask, render_template, request, jsonify, send_file
import google.generativeai as genai
from fpdf import FPDF
from bs4 import BeautifulSoup
import requests
import os
from secret import GEMINI_API_KEY, GOOGLE_MAPS_API_KEY  # Import API keys from secret.py

app = Flask(__name__)

def setup_gemini():
    try:
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set")
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-pro-latest")  # Using stable version
        # Test the configuration
        test_response = model.generate_content("Test")
        if test_response.text:
            print("Gemini API configured successfully")
            return model
        else:
            raise Exception("Gemini API test failed")
    except Exception as e:
        print(f"Error configuring Gemini API: {str(e)}")
        return None

# Initialize the model
model = setup_gemini()

# Load Scholarship Data 
scholarships = [
    {"name": "UNICEF Education Grant", "eligibility": "High school students, low-income", "apply": "https://www.unicef.org/"},
    {"name": "Google Scholarship", "eligibility": "Students in STEM", "apply": "https://buildyourfuture.withgoogle.com/scholarships"},
    {"name": "Local Aid", "eligibility": "Residents of rural areas", "apply": "https://example.com"},
    {"name": "Fund for Education Abroad", "eligibility": "College", "apply": "https://fundforeducationabroad.org/"},
    {"name": "Golden Key Scholarships", "eligibility": "College", "apply": "https://www.goldenkey.org/scholarships/"},
    {"name": "Rotary Foundation Global Scholarship Grants", "eligibility": "College", "apply": "https://www.rotary.org/en/our-programs/scholarships"},
    {"name": "The NextGen Scholarship", "eligibility": "High school students, low-income", "apply": "https://www.perkconsulting.net/about/nextgen/"}
]
            
subjects = {
    "Programming": [
        ("CS50, Harvard", "https://cs50.harvard.edu/"),
        ("Python.org", "https://www.python.org/"),
        ("freeCodeCamp", "https://www.freecodecamp.org/")
    ],
    "Math": [
        ("Khan Academy", "https://www.khanacademy.org/"),
        ("Harvard University", "https://pll.harvard.edu/subject/mathematics/free"),
        ("The Open University", "https://www.open.edu/openlearn/science-maths-technology/free-courses")
    ],
    "Science": [
        ("Stanford University", "https://ughb.stanford.edu/courses/approved-courses/science-courses-2024-25"),
        ("Yale College", "https://science.yalecollege.yale.edu/academics/faculty-resources/science-courses-without-prerequisite")
    ]
}

chat_history = []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/mentor')
def mentor():
    return render_template('mentor.html', messages=chat_history)

@app.route('/resources')
def resources():
    return render_template('resources.html', subjects=subjects, scholarships=scholarships)

@app.route('/resume-builder')
def resume_builder():
    return render_template('resume.html')

@app.route('/support')
def support():
    return render_template('support.html', google_maps_api_key=GOOGLE_MAPS_API_KEY)

@app.route('/community')
def community():
    # Dummy data for community features
    mentors = [
        {
            "name": "Harvard Professor Lecture ",
            "expertise": "Computer Science",
            "video_url": "https://youtu.be/LfaMVlDaQ24?si=Gh7gwKP_TR3AIYjL",
            "availability": "Mon, Wed, Fri",
            "rating": 4.9
        },
        {
            "name": "FreeCodeCamp Lecture",
            "expertise": "Data Science",
            "video_url": "https://youtu.be/ua-CiDNNj30?si=ttqb1oShO8mZ4r8Y",
            "availability": "Tue, Thu",
            "rating": 4.8
        },
        {
            "name": "MIT 6.006 Introduction to Algorithms, Spring 2020",
            "expertise": "Computer Science",
            "video_url": "https://youtube.com/playlist?list=PLUl4u3cNGP63EdVPNLG3ToM6LaEUuStEY&si=8xdesLsiGoBEQanj",
            "availability": "Mon-Fri",
            "rating": 4.7
        }
    ]
    
    study_groups = [
        {
            "name": "Python Programming",
            "members": 25,
            "meeting_time": "Mondays 7 PM EST",
            "level": "Intermediate",
            "current_topic": "Data Structures"
        },
        {
            "name": "Machine Learning",
            "members": 18,
            "meeting_time": "Wednesdays 6 PM EST",
            "level": "Advanced",
            "current_topic": "Neural Networks"
        },
        {
            "name": "Web Development",
            "members": 30,
            "meeting_time": "Tuesdays 8 PM EST",
            "level": "Beginner",
            "current_topic": "JavaScript Basics"
        }
    ]
    
    support_resources = [
        {
            "title": "Career Path Planning",
            "counselor": "Lisa Thompson",
            "duration": "45 minutes",
            "focus": "Tech Industry",
            "video_url": ""
        },
        {
            "title": "Resume Review",
            "counselor": "Michael Brown",
            "duration": "30 minutes",
            "focus": "Job Applications",
            "video_url": ""
        },
        {
            "title": "Interview Preparation",
            "counselor": "David Garcia",
            "duration": "60 minutes",
            "focus": "Technical Interviews",
            "video_url": ""
        }
    ]
    
    return render_template('community.html', 
                         mentors=mentors, 
                         study_groups=study_groups, 
                         support_resources=support_resources)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    prompt = data.get('message')
    
    if not prompt or not isinstance(prompt, str):
        return jsonify({"error": "Invalid or missing message"}), 400
        
    if len(prompt.strip()) == 0:
        return jsonify({"error": "Message cannot be empty"}), 400
    
    chat_history.append({"role": "user", "content": prompt})
    try:
        # Enhanced prompt for structured bullet point responses
        structured_prompt = f"""
        As an AI Career Mentor, provide a detailed response to: {prompt}

        Format your entire response in bullet points following these rules:
        1. Start with a brief overview bullet point
        2. Break down all information into clear, concise bullet points
        3. Use "•" for main points
        4. Use "◦" for sub-points
        5. Use "◆" for important highlights
        6. Group similar information together
        7. Keep each bullet point focused and easy to read
        8. Do not use markdown formatting
        9. Add emojis at the start of relevant bullet points
        10. End with action items or next steps

        Example format:
        • Overview: [Brief context]
        ◦ Key point 1
        ◦ Key point 2
        • Main topic:
        ◦ Detail 1
        ◦ Detail 2
        ◆ Important highlight
        • Next steps:
        ◦ Action item 1
        ◦ Action item 2

        Make the response visually organized and easy to follow.
        """
        
        response = model.generate_content(structured_prompt)
        if not response.text:
            raise Exception("Empty response from AI model")
            
        ai_response = response.text
        # Format the response with proper HTML spacing
        ai_response = f'<div style="line-height: 1.8;">{ai_response}</div>'
        
        chat_history.append({"role": "assistant", "content": ai_response})
        return jsonify({"response": ai_response})
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")  # Add logging
        # Remove the failed message from chat history
        if len(chat_history) > 0 and chat_history[-1]["role"] == "user":
            chat_history.pop()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/api/generate-resume', methods=['POST'])
def generate_resume():
    data = request.json
    required_fields = ['name', 'education', 'skills', 'experience', 'projects']
    
    # Check for missing fields
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"})
    
    name = data.get('name')
    education = data.get('education')
    skills = data.get('skills')
    experience = data.get('experience')
    projects = data.get('projects')
    
    prompt = f"""
        Create a professional resume for the following details:
        - Name: {name}
        - Education: {education}
        - Skills: {skills}
        - Experience: {experience}
        - Projects: {projects}
        Format it as a well-structured resume with sections and proper formatting.
        """
    
    try:
        response = model.generate_content(prompt)
        return jsonify({"resume": response.text})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/summarize-course', methods=['POST'])
def summarize_course():
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({"error": "No URL provided"})
    
    # Basic URL validation
    if not url.startswith(('http://', 'https://')):
        return jsonify({"error": "Invalid URL format. URL must start with http:// or https://"})
    
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)  # Add timeout
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            paragraphs = soup.find_all("p")
            text_content = "\n".join([p.get_text() for p in paragraphs if p.get_text()])
            
            if not text_content:
                return jsonify({"error": "No content found on the provided URL"})
            
            summary = model.generate_content(f"Summarize this course content in bullet points:\n{text_content[:5000]}")
            return jsonify({"summary": summary.text})
        else:
            return jsonify({"error": f"Failed to fetch course content. Status code: {response.status_code}"})
    except requests.Timeout:
        return jsonify({"error": "Request timed out. Please try again."})
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to fetch course content: {str(e)}"})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/search', methods=['POST'])
def search_api():
    data = request.json
    if not data or 'query' not in data:
        return jsonify({"error": "No search query provided"}), 400
    
    query = data.get('query').lower()
    filter_type = data.get('filter', 'all')
    
    results = []
    
    # Search in courses
    if filter_type in ['all', 'courses']:
        for subject, courses in subjects.items():
            for course_name, course_url in courses:
                if query in course_name.lower() or query in subject.lower():
                    results.append({
                        "title": course_name,
                        "url": course_url,
                        "description": f"Free online course from {subject}",
                        "type": "course",
                        "rating": "4.8",
                        "userCount": "10k+",
                        "lastUpdated": "2024"
                    })
    
    # Search in scholarships
    if filter_type in ['all', 'scholarships']:
        for scholarship in scholarships:
            if query in scholarship['name'].lower() or query in scholarship['eligibility'].lower():
                results.append({
                    "title": scholarship['name'],
                    "url": scholarship['apply'],
                    "description": f"Eligibility: {scholarship['eligibility']}",
                    "type": "scholarship",
                    "rating": "4.5",
                    "userCount": "500+",
                    "lastUpdated": "2024"
                })
    
    return jsonify({
        "results": results,
        "total": len(results),
        "query": query,
        "filter": filter_type
    })

@app.route('/api/search-learning-centers', methods=['POST'])
def search_learning_centers():
    data = request.json
    if not data or 'location' not in data:
        return jsonify({"error": "Location is required"}), 400
        
    location = data['location']
    try:
        # Use Google Places API to search for learning centers
        search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            'query': f'learning center tuition center education center in {location}',
            'key': GOOGLE_MAPS_API_KEY
        }
        
        response = requests.get(search_url, params=params)
        if response.status_code == 200:
            results = response.json()
            return jsonify(results)
        else:
            return jsonify({"error": "Failed to fetch learning centers"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Use environment variable for port with a default of 5000
    port = int(os.environ.get('PORT', 5000))
    # In production, debug should be False
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
