# Repository Quality Analyzer

This project is an automated code quality analyzer designed for public GitHub repositories. It assesses the source code (primarily tailored for Java applications) and provides detailed metrics on software engineering principles. The analysis covers:

- Cyclomatic Complexity
- Coupling Between Objects (CBO)
- Code Duplication
- Test Coverage Tracking

The application is split into two parts: a React frontend powered by Vite, and a FastAPI backend written in Python.

## Prerequisites

- Node.js
- Python 3.x

## Setup and Installation

### Backend (Python)

1. Navigate to the python directory:
   `cd python`

2. Install the required dependencies using the generated requirements.txt:
   `pip install -r requirements.txt`

3. Start the FastAPI development server:
   `uvicorn app.main:app --reload`
   (The server will typically run at http://localhost:8000)

### Frontend (React / Vite)

1. Navigate to the analyzer directory:
   `cd analyzer`

2. Install the Node package dependencies:
   `npm install`

3. Start the Vite development server:
   `npm run dev`
   (The frontend will typically run at http://localhost:5173)

## Usage

1. Start both the frontend and backend servers.
2. Access the frontend application in your web browser.
3. Paste a public GitHub repository URL (e.g., https://github.com/user/repo) into the input field and submit.
4. Click the analysis button to process the repository code and evaluate its metrics.
5. Export or view the generated HTML report directly from the interface.