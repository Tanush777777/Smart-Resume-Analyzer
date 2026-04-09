# How to Run Smart Resume Analyzer in VS Code

## 🚀 Quick Start

### Method 1: Using VS Code Terminal (Easiest)

1. **Open the Project in VS Code**
   - Open VS Code
   - File → Open Folder
   - Select your project folder: `mini p`

2. **Open Terminal in VS Code**
   - Press `` Ctrl + ` `` (backtick) to open terminal
   - Or go to: Terminal → New Terminal

3. **Run the Server**
   - In the terminal, type:
     ```bash
     py app.py
     ```
   - Press Enter

4. **Wait for Server to Start**
   - You'll see: `* Running on http://0.0.0.0:5000`
   - Server is now running!

5. **Open in Browser**
   - Go to: `http://localhost:5000`
   - The website should load!

---

### Method 2: Using VS Code Debugger (Advanced)

1. **Open the Project**
   - Open VS Code
   - File → Open Folder → Select `mini p` folder

2. **Start Debugging**
   - Press `F5` OR
   - Go to: Run → Start Debugging
   - Select: "Python: Flask" from the dropdown

3. **Server Starts Automatically**
   - VS Code will start the Flask server
   - Check the Debug Console for output
   - You'll see: `* Running on http://0.0.0.0:5000`

4. **Open in Browser**
   - Go to: `http://localhost:5000`

---

## 📋 Step-by-Step Guide

### Step 1: Install Python Extension (if not installed)

1. Open VS Code
2. Click Extensions icon (or press `Ctrl + Shift + X`)
3. Search for "Python"
4. Install "Python" extension by Microsoft

### Step 2: Open Your Project

1. File → Open Folder
2. Navigate to: `C:\Users\sreec\OneDrive\Desktop\mini p`
3. Click "Select Folder"

### Step 3: Select Python Interpreter

1. Press `Ctrl + Shift + P`
2. Type: "Python: Select Interpreter"
3. Choose your Python version (Python 3.x)

### Step 4: Run the Application

**Option A: Terminal Method**
```
1. Open Terminal (Ctrl + `)
2. Type: py app.py
3. Press Enter
4. Wait for "Running on http://0.0.0.0:5000"
5. Open browser: http://localhost:5000
```

**Option B: Debug Method**
```
1. Press F5
2. Select "Python: Flask"
3. Server starts automatically
4. Open browser: http://localhost:5000
```

---

## 🎯 VS Code Features You Can Use

### Integrated Terminal
- **Open**: `` Ctrl + ` ``
- **New Terminal**: Terminal → New Terminal
- **Split Terminal**: `` Ctrl + Shift + ` ``

### Debugging
- **Set Breakpoints**: Click left of line numbers
- **Start Debugging**: `F5`
- **Stop Debugging**: `Shift + F5`
- **Step Over**: `F10`
- **Step Into**: `F11`

### Code Navigation
- **Go to Definition**: `F12`
- **Find All References**: `Shift + F12`
- **Quick Open File**: `Ctrl + P`

---

## ⚙️ VS Code Settings (Optional)

Create `.vscode/settings.json` for custom settings:

```json
{
    "python.defaultInterpreterPath": "py",
    "python.terminal.activateEnvironment": true,
    "files.autoSave": "afterDelay",
    "files.autoSaveDelay": 1000
}
```

---

## 🐛 Troubleshooting

### Python Not Found
- Install Python from python.org
- Or use: `python app.py` instead of `py app.py`

### Module Not Found
- Open terminal in VS Code
- Run: `py -m pip install -r requirements.txt`

### Port Already in Use
- Close other terminal windows
- Or change port in `app.py` (line 538): `port=5001`

### Terminal Not Opening
- View → Terminal
- Or press: `` Ctrl + ` ``

---

## 💡 Tips

1. **Keep Terminal Open**: The server must stay running
2. **Auto-Save**: Enable auto-save in VS Code settings
3. **Live Reload**: Flask auto-reloads on code changes (in debug mode)
4. **Multiple Terminals**: You can have multiple terminals open
5. **Integrated Browser**: Use VS Code's built-in browser preview (optional extension)

---

## 📝 Quick Commands Reference

| Action | Shortcut |
|--------|----------|
| Open Terminal | `` Ctrl + ` `` |
| Start Debugging | `F5` |
| Stop Debugging | `Shift + F5` |
| Run Python File | `Ctrl + F5` |
| Open Command Palette | `Ctrl + Shift + P` |

---

**Happy Coding! 🎉**



