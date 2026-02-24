# Mahil Techlab Django Web Application

Production-ready Django + PostgreSQL web application for an IT company and training platform.

Web users do not need to install anything. If needed, they can download and install the MahilMart POS desktop app.

Full project documentation:

- `docs/FULL_DOCUMENTATION.md`

## Core Features

- Responsive public pages: Home, Courses, Contact
- Home page slider with database-managed image uploads
- Contact form stores messages and emails them to your configured inbox
- Registration + Login + Google Login
- Protected course application flow (login required)
- Inno Setup installer download button for MahilMart POS
- Projects portfolio pages with install + details view
- Superuser-only unified admin dashboard
  - Messages, courses, and users in one page
  - URL: `/admin-access/dashboard/`
- Superuser-only custom user management page
  - Add, edit, delete users
  - URL: `/admin-access/users/`
- Superuser-only contact message inbox page
  - View all incoming contact form messages
  - URL: `/admin-access/messages/`
- Django admin support

## Live Deployment (No User Installation)

### Option A: Render (recommended)

This repo includes `render.yaml` (blueprint deployment).

1. Push project to GitHub.
2. In Render, create a new Blueprint and select your repo.
3. Render will create:
   - Web service (`mahil-techlab-web`)
   - PostgreSQL database (`mahil-techlab-db`)
4. In Render environment variables, set:
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`
5. After first deploy, open Render shell and run:
   - `python manage.py createsuperuser`
6. Open your live URL.

Note:
- Update `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` for your real domain.
- Update Google OAuth redirect URI to:
  - `https://<your-domain>/accounts/google/login/callback/`

### Option B: Docker (server/VPS)

This repo includes `Dockerfile`, `docker-compose.yml`, and `entrypoint.sh`.

Run:

```bash
docker compose up --build
```

Then open:
- `http://127.0.0.1:8000`

## Local Development (without Docker)

1. Create venv:
   - `python -m venv .venv`
   - `.venv\Scripts\Activate.ps1`
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Configure `.env` from `.env.example`
4. Run migrations:
   - `python manage.py migrate`
5. Seed courses (optional):
   - `python manage.py seed_courses`
6. Seed projects (optional):
   - `python manage.py seed_projects`
7. Create admin:
   - `python manage.py createsuperuser`
8. Run:
   - `python manage.py runserver`

## Important URLs

- Home: `http://127.0.0.1:8000/`
- Health check: `http://127.0.0.1:8000/healthz/`
- Projects: `http://127.0.0.1:8000/projects/`
- Login: `http://127.0.0.1:8000/login/`
- Register: `http://127.0.0.1:8000/register/`
- Google login: `http://127.0.0.1:8000/accounts/google/login/`
- Django admin: `http://127.0.0.1:8000/admin/`
- Admin dashboard: `http://127.0.0.1:8000/admin-access/dashboard/`
  - Includes Messages, Home Slider, Courses, and Users panels
- Custom admin users: `http://127.0.0.1:8000/admin-access/users/`
- Contact messages inbox: `http://127.0.0.1:8000/admin-access/messages/`
- POS installer download: `http://127.0.0.1:8000/downloads/mahilmart-pos/setup/`
  - Login required before download

## Environment Variables

- `SECRET_KEY`
- `DEBUG`
- `ALLOW_ALL_HOSTS` (`True` to allow any IP/host without hardcoding)
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`
- `MAX_LOGIN_ATTEMPTS` (failed login attempts before temporary lockout)
- `LOGIN_LOCKOUT_SECONDS` (lockout duration in seconds)
- `DATABASE_URL` (preferred in production)
- `SESSION_COOKIE_HTTPONLY`
- `CSRF_COOKIE_HTTPONLY`
- `SESSION_COOKIE_SAMESITE`
- `CSRF_COOKIE_SAMESITE`
- `SECURE_CONTENT_TYPE_NOSNIFF`
- `X_FRAME_OPTIONS`
- `SECURE_REFERRER_POLICY`
- `SECURE_CROSS_ORIGIN_OPENER_POLICY`
- `SECURE_CROSS_ORIGIN_RESOURCE_POLICY`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `EMAIL_BACKEND`
- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_USE_TLS`
- `EMAIL_USE_SSL`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `DEFAULT_FROM_EMAIL`
- `SERVER_EMAIL`
- `CONTACT_RECEIVER_EMAIL` (your inbox for contact form notifications)
- `POS_INSTALLER_PATH` (local `.exe` path, default points to `~/Documents/GitHub/mahilmart-pos/installer/output/MahilMartPOS-Setup.exe`)
- `POS_INSTALLER_URL` (optional external download URL, e.g. GitHub Releases)
- `POS_INSTALLER_FILENAME`

## Security Notes

- Frontend code (HTML/CSS/JS) is always visible in browsers; this is normal for all websites.
- Keep secrets and sensitive logic on backend only (env vars + server code).
- In production, set `DEBUG=False`, keep `ALLOW_ALL_HOSTS=False`, and use strict `ALLOWED_HOSTS`.

## Inno Setup Installer Flow

1. Build your POS installer in `mahilmart-pos` using your `.iss` file.
2. Confirm `.exe` exists (example):
   - `C:\Users\Billing System 2\Documents\GitHub\mahilmart-pos\installer\output\MahilMartPOS-Setup.exe`
3. Keep `POS_INSTALLER_PATH` pointing to that file.
4. Logged-in users can install from project/home pages or directly via `/downloads/mahilmart-pos/setup/`.

## Allow Any IP (No Hardcoding)

Use in `.env`:

```env
ALLOW_ALL_HOSTS=True
```

This sets Django `ALLOWED_HOSTS` to `*`.
