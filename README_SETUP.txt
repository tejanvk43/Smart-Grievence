==============================================================================
                    SMART GRIEVANCE SYSTEM - SETUP INSTRUCTIONS
==============================================================================

PREREQUISITES:
1. Python 3.8 or higher installed and added to PATH.
2. Node.js (v14 or higher) and npm installed.

------------------------------------------------------------------------------
AUTOMATED SETUP (WINDOWS):
------------------------------------------------------------------------------
1. Double-click 'setup_project.bat'.
   - This will create a python virtual environment, install python libraries, download NLTK data, and install node modules.
   
2. Double-click 'run_project.bat'.
   - This will launch two command windows: one for the Flask backend and one for the React frontend.
   - The app should open or be accessible at http://localhost:3000.

------------------------------------------------------------------------------
MANUAL SETUP (COMMAND LINE):
------------------------------------------------------------------------------
If you prefer running commands manually or are on Mac/Linux:

1. Backend Setup:
   cd backend
   python -m venv venv                 # Create virtual env
   # Windows: venv\Scripts\activate    # Activate env
   # Mac/Linux: source venv/bin/activate
   pip install -r requirements.txt     # Install requirements
   python download_nltk.py             # Download NLTK data
   python app.py                       # Start Server

2. Frontend Setup:
   # in the root folder
   npm install                         # Install dependencies
   npm run dev                         # Start setup server

3. Configuration:
   - Ensure 'backend/.env' exists. If not, copy 'backend/.env.example' to 'backend/.env'.
   - Default SQLite database will be created automatically.

------------------------------------------------------------------------------
TROUBLESHOOTING:
------------------------------------------------------------------------------
- If backend fails with "Module not found", ensure the virtual environment is activated.
- If frontend fails to connect to backend, ensure backend is running at port 5000.
