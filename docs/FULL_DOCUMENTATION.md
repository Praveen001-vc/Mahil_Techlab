# Mahil Techlab - Full Project Documentation

Last updated: February 21, 2026

## 1) Project Overview

Mahil Techlab is a Django + PostgreSQL web application for:

- IT services company presentation
- IT course listing and enrollment
- User authentication with username/password and Google login
- Project portfolio pages with details and installer actions
- Superuser user-management panel (add/edit/delete users)
- Download gateway for MahilMart POS installer (login required)

The app is responsive and works across mobile, tablet, laptop, and large screens.

## 2) Technology Stack

- Backend: Django 5.2.4
- Database: PostgreSQL
- Authentication: Django auth + django-allauth (Google OAuth)
- Static files in production: WhiteNoise
- WSGI server: Gunicorn
- Deployment options: Render / Docker / VPS

Python dependencies are in `requirements.txt`.

## 3) Repository Structure

- `config/` - Django project settings and root URLs
- `core/` - Main app (models, views, forms, URLs, admin, commands)
- `templates/` - HTML templates
- `static/` - CSS and JavaScript
- `Dockerfile`, `docker-compose.yml`, `entrypoint.sh` - container deployment
- `render.yaml` - Render blueprint deployment
- `docs/FULL_DOCUMENTATION.md` - this document

## 4) Functional Modules

### 4.1 Public Website Pages

- Home page
- Projects listing and project detail pages
- Courses page
- Contact page

### 4.2 Authentication

- Register page
- Login page
- Logout
- Google OAuth login via `django-allauth`
- Password visibility toggle in auth forms

### 4.3 Courses and Enrollment

- Courses are publicly visible
- Enrollment submission requires login
- Enrollment records are linked to logged-in user

### 4.4 Projects Portfolio

- Project card includes name, icon, short description, version, and actions
- Project detail page includes full details text
- Install button behavior:
- Logged-in users can get install link
- Logged-out users see "Login to Install"

### 4.5 Installer Download Gateway

- Route: `/downloads/mahilmart-pos/setup/`
- Access rule: authenticated users only
- Download behavior:
- If `POS_INSTALLER_URL` exists, redirect to that URL
- Else stream local file from `POS_INSTALLER_PATH`

### 4.6 Superuser User Management

- Route: `/admin-access/users/`
- Features:
- List/search users
- Add user
- Edit user
- Delete user
- Safety checks:
- Cannot delete own logged-in account
- Cannot remove the last superuser

## 5) URL Map

### 5.1 Core Routes

- `/` -> Home
- `/projects/` -> Projects list
- `/projects/<slug>/` -> Project detail
- `/courses/` -> Courses + enrollment form
- `/contact/` -> Contact form
- `/register/` -> Register
- `/login/` -> Login
- `/logout/` -> Logout
- `/downloads/mahilmart-pos/setup/` -> Installer download (login required)
- `/admin-access/users/` -> Superuser user manager
- `/admin-access/users/<id>/edit/` -> Edit user
- `/admin-access/users/<id>/delete/` -> Delete user
- `/healthz/` -> Health check

### 5.2 Built-in/Admin Routes

- `/admin/` -> Django admin
- `/accounts/*` -> allauth routes (Google login and social account pages)

## 6) Data Model Reference

### 6.1 `Course`

- `title` (unique)
- `slug` (unique)
- `description`
- `duration_weeks`
- `level` (Beginner/Intermediate/Advanced)
- `fee_usd`
- `is_active`
- `created_at`

### 6.2 `ContactMessage`

- `name`
- `email`
- `company`
- `message`
- `created_at`

### 6.3 `Enrollment`

- `name`
- `email`
- `phone`
- `user` (FK to auth user, nullable)
- `course` (FK to Course)
- `experience`
- `notes`
- `created_at`

### 6.4 `Project`

- `name` (unique)
- `slug` (unique)
- `icon_url`
- `tagline`
- `short_description`
- `details`
- `install_url`
- `version`
- `is_active`
- `display_order`
- `created_at`

## 7) Environment Variables

### 7.1 Core

- `SECRET_KEY`
- `DEBUG`
- `TIME_ZONE`
- `SITE_ID`
- `LOGIN_REDIRECT_URL`
- `LOGOUT_REDIRECT_URL`

### 7.2 Host and CSRF

- `ALLOW_ALL_HOSTS`
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`

Notes:

- If `ALLOW_ALL_HOSTS=True`, Django sets `ALLOWED_HOSTS=["*"]`.
- For production, use specific hostnames and trusted origins.

### 7.3 Database

- Preferred: `DATABASE_URL`
- Or manual:
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_HOST`
- `POSTGRES_PORT`

### 7.4 Google OAuth

- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`

### 7.5 Installer Integration

- `POS_INSTALLER_PATH`
- `POS_INSTALLER_URL`
- `POS_INSTALLER_FILENAME`

## 8) Local Setup (Windows / PowerShell)

1. Create and activate virtual environment.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Install dependencies.

```powershell
pip install -r requirements.txt
```

3. Copy env template and edit.

```powershell
Copy-Item .env.example .env
```

4. Run migrations.

```powershell
python manage.py migrate
```

5. Optional seed data.

```powershell
python manage.py seed_courses
python manage.py seed_projects
```

6. Create superuser.

```powershell
python manage.py createsuperuser
```

7. Start server.

```powershell
python manage.py runserver 0.0.0.0:8000
```

## 9) PostgreSQL Setup Notes

Default DB name used in project:

- `mahil_techlab`

If manual DB creation is required:

```sql
CREATE DATABASE mahil_techlab;
```

Then update `.env` with the correct PostgreSQL credentials.

## 10) Google OAuth Configuration (Important)

In Google Cloud Console:

1. Create OAuth client (Web application).
2. Add Authorized JavaScript Origins:
- `http://127.0.0.1:8000`
- `http://localhost:8000`
- `https://<your-production-domain>`
3. Add Authorized Redirect URIs:
- `http://127.0.0.1:8000/accounts/google/login/callback/`
- `http://localhost:8000/accounts/google/login/callback/`
- `https://<your-production-domain>/accounts/google/login/callback/`
4. Put client id/secret into `.env`.

Common mistakes:

- Origins must not include path. Example invalid origin: `http://127.0.0.1:8000/accounts/...`
- If you see `Error 403: org_internal`, your OAuth app is restricted to organization users. Change audience/test users in Google OAuth consent settings.

## 11) Installer Integration (MahilMart POS)

Two supported approaches:

- Local file download through this Django app:
- Set `POS_INSTALLER_PATH` to local `.exe`
- Hosted installer link:
- Set `POS_INSTALLER_URL` to external URL (GitHub Releases/CDN)

Current installer route:

- `/downloads/mahilmart-pos/setup/`
- Requires login

If installer file is missing, user gets a flash error and returns to home.

## 12) Deployments

### 12.1 Render

- Use `render.yaml`
- Required env vars:
- `SECRET_KEY`
- `DEBUG=False`
- `DATABASE_URL` (from Render DB)
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`

After deploy:

- Run `python manage.py createsuperuser` in shell

### 12.2 Docker Compose

```bash
docker compose up --build
```

Services:

- `db` -> PostgreSQL
- `web` -> Django + Gunicorn

Entry point runs:

- `migrate`
- `collectstatic`
- optional `seed_courses` when `SEED_COURSES=1`

## 13) Admin Operation Guide

### 13.1 Django Admin

Use `/admin/` for model-level CRUD:

- Courses
- Contacts
- Enrollments
- Projects

### 13.2 Custom Superuser Page

Use `/admin-access/users/` for user operations with custom UI.

### 13.3 Create Project Detail Pages (Admin Steps)

1. Open `/admin/` and login as superuser.
2. Go to `Core -> Projects`.
3. Click `Add Project`.
4. Fill required fields:
- `name`
- `slug`
- `short_description`
5. Fill optional fields for richer detail page:
- `icon_url`
- `tagline`
- `details`
- `version`
- `install_url` (optional external installer URL)
6. Set `is_active=True` and choose `display_order`.
7. Save.
8. Open `/projects/` and `/projects/<slug>/` to verify.

## 14) Security Notes

- Set `DEBUG=False` in production.
- Use strong `SECRET_KEY`.
- Use specific hosts in `ALLOWED_HOSTS` and origins in `CSRF_TRUSTED_ORIGINS`.
- Keep cookies secure in production (`SESSION_COOKIE_SECURE=True`, `CSRF_COOKIE_SECURE=True`).
- Do not commit real secrets to git.
- Use signed installer for Windows distribution to reduce SmartScreen warnings.

## 15) Troubleshooting

### 15.1 `ModuleNotFoundError: No module named 'jwt'`

Cause: `PyJWT` not installed.
Fix:

```powershell
pip install "PyJWT[crypto]"
```

### 15.2 `ValueError ... multiple authentication backends configured`

Cause: logging in a new user without specifying backend.
Status: already fixed in `register_user` by explicitly using `ModelBackend`.

### 15.3 Google login shows "not configured yet"

Cause: missing `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` or missing SocialApp setup.
Fix: set env variables and restart server.

### 15.4 Google `org_internal` 403

Cause: OAuth app restricted to internal organization users.
Fix: adjust OAuth consent audience/test users in Google Cloud.

### 15.5 Installer download not working

Checks:

- Confirm user is logged in
- Confirm `POS_INSTALLER_URL` or valid `POS_INSTALLER_PATH`
- Confirm file exists at configured path

### 15.6 Browser warns installer is unsafe

Cause: unsigned/new executable reputation.
Fix: sign `.exe` and setup with code-signing certificate + timestamp.

## 16) Useful Commands

```powershell
python manage.py check
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_courses
python manage.py seed_projects
python manage.py collectstatic --noinput
```

## 17) Go-Live Checklist

- Set production env variables
- Set exact allowed hosts and CSRF origins
- Configure Google OAuth production URLs
- Create superuser
- Validate installer settings
- Validate login/register/enrollment/project flows
- Run `python manage.py check`
- Verify `/healthz/` returns success
