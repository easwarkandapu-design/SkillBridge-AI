# Architecture

React SPA -> Django REST Framework -> PostgreSQL.
Resume upload is processed by a service layer using PyMuPDF/python-docx. Skill extraction and matching are explainable local algorithms. Interview practice uses a role-specific question bank and rubric-based keyword coverage.

## Main entities
User (candidate/recruiter/admin), Profile, Job, Resume, Application, InterviewAttempt.

## Trust boundaries
- JWT authentication protects private APIs.
- Job creation requires recruiter/admin role.
- Applications are candidate-owned; status updates are restricted to the job owner.
- Resume upload is limited to PDF/DOCX and 5 MB in this starter.
- Uploaded documents are private to the uploading account through API filtering.

For production, add malware scanning, private object storage, signed downloads, throttling, audit logs, consent/retention policies and human review of AI outputs.
