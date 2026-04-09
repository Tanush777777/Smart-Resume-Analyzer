# How to Run Smart Resume Analyzer

## ✅ Quick Start (Windows)

### Method 1: Using the Batch File (Easiest)
1. Double-click `run.bat`
2. Wait for the server to start
3. Open your browser and go to: **http://localhost:5000**

### Method 2: Using Command Line

1. **Open PowerShell or Command Prompt** in this folder

2. **Install dependencies** (first time only):
   ```bash
   py -m pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   py app.py
   ```

4. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

## 📋 Step-by-Step Instructions

### First Time Setup:

1. **Check Python Installation**
   - Open PowerShell/Command Prompt
   - Type: `py --version`
   - Should show Python 3.x.x

2. **Install Dependencies**
   ```bash
   py -m pip install -r requirements.txt
   ```
   This installs:
   - Flask (web framework)
   - PyPDF2 (PDF processing)
   - python-docx (Word document processing)

3. **Start the Server**
   ```bash
   py app.py
   ```

4. **Access the Website**
   - Open any web browser
   - Go to: `http://localhost:5000`
   - You should see the Smart Resume Analyzer homepage

## 🎯 Using the Application

1. **Upload a Resume**
   - Click "Choose File"
   - Select a PDF, DOCX, or TXT file
   - Click "Analyze Resume"

2. **View Results**
   - See your ATS compatibility score
   - Review detected skills
   - Check suggestions for improvement

## ⚠️ Troubleshooting

### Port Already in Use
If you see "Address already in use":
- Close any other running instances
- Or change the port in `app.py` (line 178):
  ```python
  app.run(debug=True, host='0.0.0.0', port=5001)  # Change 5000 to 5001
  ```

### Python Not Found
- Make sure Python is installed
- Try `python` instead of `py`
- Or use `python3` if on Linux/Mac

### Module Not Found Errors
- Reinstall dependencies: `py -m pip install -r requirements.txt`
- Make sure you're in the correct directory

## 🛑 Stopping the Server

- Press `Ctrl + C` in the terminal where the server is running
- Or close the terminal window

## 💡 Tips

- Keep the terminal window open while using the app
- The server runs on `localhost:5000` by default
- Upload files should be under 16MB
- Supported formats: PDF, DOCX, TXT

---

**The server is now running!** 🚀
Open http://localhost:5000 in your browser to start analyzing resumes.




