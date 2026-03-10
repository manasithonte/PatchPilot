# Nexus - Agentic AI Code Upgrade Assistant

An agentic AI developer tool that automatically analyzes software repositories, identifies outdated dependencies, and generates safe upgrade patches and GitHub Pull Requests.

## Getting Started

### 1. Prerequisites
- Python 3.9+
- Node.js 18+

### 2. Setup Backend (FastAPI)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env # Add your GEMINI_API_KEY inside
uvicorn main:app --reload
```

### 3. Setup Frontend (Next.js)
```bash
cd frontend
npm install
npm run dev
```

### 4. Usage
Open `http://localhost:3000` in your browser.
Enter a valid GitHub repository URL (e.g., `https://github.com/fastapi/fastapi`) and click "Analyze Dependencies".
