# SkillBridge AI

A full-stack career and recruitment platform built with React, Django REST Framework and PostgreSQL.

## Included functionality
- JWT registration/login with candidate and recruiter roles
- Candidate profile and resume upload (PDF/DOCX)
- Resume text extraction and transparent skill detection
- Recruiter job creation and job listing
- Explainable skill-based job matching
- Job applications and recruiter application status updates
- Role-specific mock interview question bank and rubric-based feedback
- Candidate and recruiter dashboards

This is a functional portfolio project starter, not a production hiring decision system. Match scores are advisory and must not be used as automated hiring decisions. AI outputs should be reviewed by users.

## Requirements
- Python 3.11–3.13
- Node.js 20+
- PostgreSQL 14+
- Windows PowerShell (commands below also adapt to macOS/Linux)

## 1. Database
Create a PostgreSQL database:
```sql
CREATE DATABASE skillbridge_db;
```

## 2. Backend
```powershell
cd backend
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```
Edit `backend/.env` with your PostgreSQL username/password and a new Django secret key.

Then:
```powershell
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Backend: http://127.0.0.1:8000  
API root: http://127.0.0.1:8000/api/  
Admin: http://127.0.0.1:8000/admin/

## 3. Frontend
Open a second PowerShell terminal:
```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```
Frontend: http://localhost:5173

## Demo workflow
1. Register a candidate account.
2. Upload a PDF/DOCX resume from the Resume Analyzer page.
3. Register a second account with the Recruiter role (or use a recruiter account).
4. Create a job as recruiter.
5. Return to candidate account, browse jobs and view match scores.
6. Apply to a job.
7. Log in as recruiter and update application status.
8. Open Interview Prep, choose a role and answer a question.

## API endpoints
- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `GET /api/auth/me/`
- `GET/PATCH /api/profile/`
- `GET/POST /api/jobs/`
- `GET /api/jobs/<id>/`
- `POST /api/jobs/<id>/apply/`
- `GET /api/applications/`
- `PATCH /api/applications/<id>/status/`
- `POST /api/resumes/upload/`
- `GET /api/resumes/`
- `GET /api/resumes/<id>/analysis/`
- `GET /api/matching/recommendations/`
- `GET /api/interviews/questions/?role=Frontend%20Developer&level=Intermediate`
- `POST /api/interviews/evaluate/`
- `GET /api/dashboard/`

## AI implementation notes
The included engine uses local, explainable NLP-style processing:
- Resume extraction: PyMuPDF and python-docx
- Skill extraction: curated skill dictionary and normalized text matching
- Matching: weighted overlap score with matched/missing skill explanations
- Interview evaluation: rubric/keyword coverage feedback

No paid API key is required. You can later add a hosted LLM or local transformer model behind the service layer without changing the frontend API contract.

## Security and production checklist
Before production use:
- Set `DEBUG=False`, configure `ALLOWED_HOSTS`, HTTPS and secure cookie settings.
- Use a strong unique `SECRET_KEY`; never commit `.env`.
- Configure object storage for uploaded resumes, malware scanning and retention/deletion policies.
- Add email verification, password reset email delivery, rate limiting and audit logs.
- Use a managed PostgreSQL database with backups.
- Add background processing for large resume files.
- Review privacy/consent requirements for resumes and candidate data.
- Add comprehensive tests and monitoring.
- Do not use match scores as automatic hiring decisions.
