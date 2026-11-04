# API quick reference

Base URL: `/api/`

Auth:
- POST `auth/register/` {username,email,password,role,company_name?}
- POST `auth/login/` {username: email,password}
- POST `auth/token/refresh/` {refresh}
- GET `auth/me/`

Candidate:
- GET/PATCH `profile/`
- POST `resumes/upload/` multipart `file`
- GET `resumes/`
- GET `resumes/{id}/analysis/`
- GET `matching/recommendations/`
- POST `jobs/{id}/apply/`
- GET `applications/`
- GET `interviews/questions/?role=Frontend%20Developer&level=Intermediate`
- POST `interviews/evaluate/` {role,level,question,answer}

Recruiter:
- GET/POST `jobs/`
- GET `applications/`
- PATCH `applications/{id}/status/` {status}
- GET `dashboard/`
