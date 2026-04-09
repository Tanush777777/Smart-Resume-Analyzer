Smart Resume Analyzer
An AI-powered web application that analyzes resumes and provides intelligent insights, ATS compatibility scores, and actionable suggestions for improvement.

Features
🤖 AI-Powered Analysis
ATS Compatibility Score: Get a percentage score indicating how well your resume will pass through Applicant Tracking Systems
Skills Detection: Automatically identifies technical skills and competencies
Contact Information Extraction: Extracts emails and phone numbers
Experience Analysis: Detects years of experience and mentioned job titles
Section Recognition: Identifies and extracts key resume sections (Summary, Experience, Education, Skills)
💡 Intelligent Suggestions
Personalized recommendations for resume improvement
Missing information alerts
Format and content optimization tips
Action verb suggestions
Quantifiable results recommendations
📊 Comprehensive Statistics
Word and character count
Skills count
Resume structure analysis
Technology Stack
Backend: Python Flask
Frontend: HTML5, CSS3, JavaScript (Vanilla)
File Processing: PyPDF2, python-docx
AI Features: Custom NLP algorithms with regex patterns and intelligent text analysis
Installation
Prerequisites
Python 3.8 or higher
pip (Python package manager)
Setup Steps
Clone or download this repository

Create a virtual environment (recommended):

python -m venv venv
Activate the virtual environment:

On Windows:
venv\Scripts\activate
On macOS/Linux:
source venv/bin/activate
Install dependencies:

pip install -r requirements.txt
Run the application:
python app.py
Open your browser and navigate to:
http://localhost:5000
Usage
Upload Your Resume:

Click "Choose File" and select your resume (PDF, DOCX, or TXT format)
Click "Analyze Resume" button
View Results:

See your ATS compatibility score
Review detected skills and contact information
Check experience analysis and statistics
Read AI-powered suggestions for improvement
Explore extracted resume sections
Improve Your Resume:

Follow the suggestions provided
Address missing information
Optimize your resume based on the analysis
Supported File Formats
PDF (.pdf)
Microsoft Word (.docx)
Plain Text (.txt)
File Size Limit
Maximum file size: 16MB

Project Structure
smart-resume-analyzer/
│
├── app.py                 # Flask backend application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
│
├── templates/
│   └── index.html        # Main HTML template
│
├── static/
│   ├── css/
│   │   └── style.css     # Stylesheet
│   └── js/
│       └── main.js       # Frontend JavaScript
│
└── uploads/              # Temporary file storage (auto-created)
Features in Detail
ATS Score Calculation
The ATS (Applicant Tracking System) score is calculated based on:

Presence of contact information (email, phone)
Skills listed
Experience clearly stated
Education section present
Appropriate resume length
Keyword optimization
Skills Detection
The system recognizes over 30 common technical skills including:

Programming languages (Python, JavaScript, Java, etc.)
Frameworks (React, Django, Flask, etc.)
Tools and technologies (AWS, Docker, Git, etc.)
Methodologies (Agile, Scrum, DevOps, etc.)
Smart Suggestions
The AI analyzes your resume and provides:

Error-level: Critical missing information
Warning-level: Important improvements needed
Info-level: Optimization tips and best practices
Customization
Adding More Skills
Edit the tech_skills list in app.py to add more skills for detection.

Modifying ATS Score Calculation
Adjust the ats_factors dictionary in the analyze_resume() function to change scoring criteria.

Styling
Modify static/css/style.css to customize the appearance.

Troubleshooting
File Upload Issues
Ensure the file is in a supported format (PDF, DOCX, TXT)
Check file size (must be under 16MB)
Verify the file is not corrupted
Analysis Errors
Make sure the resume contains readable text (not just images)
For PDFs, ensure text is selectable (not scanned images)
Try converting to DOCX or TXT format if issues persist
Port Already in Use
If port 5000 is already in use, modify the port in app.py:

app.run(debug=True, host='0.0.0.0', port=5001)  # Change 5000 to another port
Future Enhancements
Potential features for future versions:

Integration with OpenAI GPT for advanced analysis
Resume comparison with job descriptions
Export analysis report as PDF
Resume templates and builder
Multi-language support
Cloud storage integration
Resume version history
