# Mahil Techlab Django Web Application

Production-ready Django + PostgreSQL web application for an IT company and training platform.

Web users do not need to install anything. If needed, they can download and install the MahilMart POS desktop app.

Full project documentation:

- `docs/FULL_DOCUMENTATION.md`

## Core Features

- Responsive public pages: Home, Courses, Contact
- Registration + Login + Google Login
- Protected course application flow (login required)
- Inno Setup installer download button for MahilMart POS
- Projects portfolio pages with install + details view
- Superuser-only custom user management page
  - Add, edit, delete users
  - URL: `/admin-access/users/`
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
- Custom admin users: `http://127.0.0.1:8000/admin-access/users/`
- POS installer download: `http://127.0.0.1:8000/downloads/mahilmart-pos/setup/`
  - Login required before download

## Environment Variables

- `SECRET_KEY`
- `DEBUG`
- `ALLOW_ALL_HOSTS` (`True` to allow any IP/host without hardcoding)
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`
- `DATABASE_URL` (preferred in production)
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `POS_INSTALLER_PATH` (local `.exe` path, default points to `~/Documents/GitHub/mahilmart-pos/installer/output/MahilMartPOS-Setup.exe`)
- `POS_INSTALLER_URL` (optional external download URL, e.g. GitHub Releases)
- `POS_INSTALLER_FILENAME`

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
