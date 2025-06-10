# 🍝 Pasta Timer

A simple Python app to help you cook pasta perfectly every time! Just select your pasta type and let the timer do the rest.

## 📋 What You Need

Before starting, make sure you have:
- Python installed on your computer (version 3.7 or higher)
- Git installed (to download this project)

### Check if Python is installed:
Open your terminal/command prompt and type:
```bash
python --version
```
If you see something like "Python 3.9.0", you're good to go! If not, download Python from [python.org](https://python.org).

## 🚀 Getting Started

### Step 1: Download the Project
```bash
git clone https://github.com/lampealex888/pasta-timer.git
cd pasta-timer
```

### Step 2: Create a Virtual Environment
A virtual environment keeps this project's files separate from other Python projects on your computer.

**On Windows:**
```bash
python -m venv pasta_timer_env
pasta_timer_env\Scripts\activate
```

**On Mac/Linux:**
```bash
python -m venv pasta_timer_env
source pasta_timer_env/bin/activate
```

✅ **You'll know it worked when you see `(pasta_timer_env)` at the beginning of your command line!**

### Step 3: Install Required Packages
```bash
pip install -r requirements.txt
```

This installs Streamlit and any other packages the app needs.

## 🎮 Running the App

### Command Line Version:
```bash
python pasta_timer.py
```

### Web Version (Streamlit):
```bash
streamlit run streamlit_app.py
```

The web version will automatically open in your browser at `http://localhost:8501`

## 🛑 When You're Done

To stop the virtual environment when you're finished:
```bash
deactivate
```

## 🆘 Troubleshooting

**"Python is not recognized"**
- Make sure Python is installed and added to your PATH
- Try using `python3` instead of `python`

**"No module named streamlit"**
- Make sure your virtual environment is activated (you should see `(pasta_timer_env)` in your terminal)
- Run `pip install streamlit` again

**Virtual environment activation not working?**
- On Windows, try: `pasta_timer_env\Scripts\activate.bat`
- Make sure you're in the project folder when running the commands

**Still stuck?**
- Make sure you're in the right folder (`cd pasta-timer`)
- Try closing your terminal and opening a new one
- Double-check that Python is installed with `python --version`

## 📁 Project Structure
```
pasta-timer/
├── pasta_timer.py         # Command line version
├── streamlit_app.py       # Web version (if created)
├── alarm.mp3              # Alarm sound file
├── requirements.txt       # List of required packages
├── .gitignore             # Files to ignore in git
├── README.md              # This file!
└── pasta_timer_env/       # Virtual environment (don't touch!)
```

## 🎯 Next Steps

- Refactor code for modularity as needed
- Add key features like custom pasta types and progress bar in the CLI
- Build a basic GUI
- Continue adding features as needed

Happy coding! 🐍✨