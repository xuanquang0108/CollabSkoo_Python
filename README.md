# CollabSkoo_Python

**Backend for CollabSkoo** — a student-focused document-sharing platform that provides secure uploads, metadata-driven search, a user reputation system, and admin moderation.

---

## Project overview
CollabSkoo helps students share and discover study materials (notes, past exams, guides).  
This repository implements a deployable backend with authentication, file upload & storage, searchable metadata, a points-based reputation system, and admin moderation endpoints.

---

## Key features
- Email/password authentication and session management  
- Secure file upload with metadata: course, lecturer, semester, tags, description  
- Search & filter endpoints (course, tags, uploader, keywords)  
- Points / rank system to reward contributors  
- Admin moderation: review and remove uploads, manage users  
- RESTful API ready for frontends  
- Simple default storage (local) and SQLite DB — easy to swap for production services

---

## Quick start (local)
> Assumes Python 3.10+. Adjust commands to match your repo structure.

```bash
# 1. clone
git clone https://github.com/xuanquang0108/CollabSkoo_Python.git
cd CollabSkoo_Python

# 2. create virtual environment
python -m venv .venv
source .venv/bin/activate   # on Linux/Mac
# or .venv\Scripts\activate  # on Windows

# 3. install dependencies
pip install -r requirements.txt

# 4. copy env and edit
cp .env.example .env
# edit .env: SECRET_KEY, DATABASE_URL, STORAGE_PATH, etc.

# 5. initialize database
python manage.py migrate
python manage.py seed   # optional: add sample data

# 6. run the server
flask run --host=0.0.0.0 --port=5000
```
## Environment variables

Create a .env file (or export variables in your shell):

```bash
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///./collabskoo.db
STORAGE_PATH=./uploads
MAX_UPLOAD_SIZE=52428800
```
## Example API endpoints
```bash
Confirm actual route names in code and update as needed.

POST /api/auth/register — register user
POST /api/auth/login — login
GET /api/files — list & search files (query params: q, course, tags, semester)
POST /api/files — upload file (multipart/form-data + metadata)
GET /api/files/:id/download — download a file
PUT /api/users/:id/points — modify user points (admin)
GET /api/admin/uploads — list pending uploads (admin)
```
## Security notes

- Sanitize and normalize filenames; never use user input directly as file paths.
- Validate allowed file types and max size before saving.
- Store secrets only in environment variables; never commit .env.
- Rate-limit upload endpoints to prevent abuse.
- Consider virus scanning (ClamAV or third-party) for uploaded files in production.

## Deployment recommendations

- Containerize using Docker and docker-compose
- Use PostgreSQL in production (instead of SQLite)
- Store file uploads in S3/MinIO/Supabase Storage and serve via signed URLs
- Add CI/CD (GitHub Actions) to run tests, linting, and migrations on PRs
- Add monitoring (Sentry) and metrics (Prometheus/Grafana)

## Roadmap

- OAuth (Google) and email verification
- Full-text search (Postgres FTS or Elasticsearch)
- File scanning + automated moderation
- Frontend SPA (React / Next.js) with profile pages and upload progress
- Analytics dashboard for admins

## Contributing

- Open an issue to discuss large changes
- Create a focused branch and submit a pull request
- Add tests for new features/bug fixes
- Use clear commit messages


## Contact
Author: xuanquang0108
