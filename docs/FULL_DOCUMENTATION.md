# Mahil Techlab - Full Project Documentation

Last updated: February 24, 2026

## 1) Project Overview

Mahil Techlab is a Django + PostgreSQL web platform that combines:

- Company website pages
- IT course catalog + enrollment
- Projects portfolio with install actions
- Contact form + email notification workflow
- Unified superuser admin dashboard

The application is responsive and includes premium home-page slider UX with autoplay, swipe support, smooth transitions, and admin-controlled slider content from database uploads.

## 2) Technology Stack

- Backend: Django 5.2.4
- Database: PostgreSQL (or `DATABASE_URL`)
- Auth: Django auth + `django-allauth` (Google)
- Images/uploads: Pillow (`ImageField`)
- Static serving (prod): WhiteNoise
- WSGI server: Gunicorn
- Deployment options: Render, Docker, VPS

Main dependencies are listed in `requirements.txt`.

## 3) Repository Structure

- `config/` - Django project configuration (`settings.py`, root URLs)
- `core/` - Main app (models, forms, views, admin, URLs, seed commands, migrations)
- `templates/` - HTML templates for website, admin dashboard, and emails
- `static/` - CSS, JavaScript, assets
- `media/` - Runtime uploaded files (home slider images)
- `docs/FULL_DOCUMENTATION.md` - this file

## 4) Implemented Modules

### 4.1 Public Website

- Home page with dynamic DB slider + featured projects/courses
- Projects list and project detail pages
- Courses page with login-protected enrollment form
- Contact page
- Health endpoint (`/healthz/`)

### 4.2 Authentication

- User registration
- Login/logout
- Google OAuth login (if configured)
- Session-based login lockout after repeated failed attempts

### 4.3 Contact + Email Notifications

- Contact submissions are saved in database
- Admin inbox is available in dashboard
- Premium HTML + text email notification sent to configured inbox
- Email includes deep link to focused message in admin dashboard
- If user is logged out, login is required before viewing admin message page

### 4.4 Unified Admin Dashboard

Single-page dashboard with tabs:

- Messages
- Enrollments
- Home Slider
- Courses
- Users

Supports create/search/manage workflows in one screen, plus separate edit pages.

### 4.5 Home Slider CMS

- Slider items managed from admin dashboard and Django admin
- Upload image, set title/subtitle/button, display order, live toggle
- Home page loads only active slider items
- Premium slider behavior includes autoplay, smooth horizontal transitions, infinite loop, dot/arrow controls, touch swipe navigation, progress bar, and pause on hover/focus.

### 4.6 Courses + Currency

- Courses support two fee currencies: `USD` (Dollar) and `INR` (Rupee)
- Dynamic symbol display in templates via model property

### 4.7 POS Installer Download Gateway

- Route: `/downloads/mahilmart-pos/setup/`
- Requires login
- Behavior: redirect to `POS_INSTALLER_URL` when present, else stream local file from `POS_INSTALLER_PATH`

## 5) URL Reference

| Path | Name | Access | Purpose |
|---|---|---|---|
| `/` | `home` | Public | Home page with DB slider |
| `/healthz/` | `healthz` | Public | Health check JSON |
| `/projects/` | `projects` | Public | Projects listing |
| `/projects/<slug>/` | `project_detail` | Public | Project detail |
| `/courses/` | `courses` | Public + Auth for submit | Course listing and enrollment |
| `/courses/enrollment-submitted/` | `enrollment_submitted` | Auth | Enrollment success details page |
| `/contact/` | `contact` | Public | Contact form |
| `/register/` | `register` | Public | User registration |
| `/login/` | `login` | Public | Login |
| `/logout/` | `logout` | Auth POST | Logout |
| `/downloads/mahilmart-pos/setup/` | `download_pos_installer` | Auth | Installer download/redirect |
| `/admin-access/dashboard/` | `admin_dashboard` | Superuser | Unified admin dashboard |
| `/admin-access/messages/` | `admin_contact_messages` | Superuser | Redirect helper to dashboard messages tab |
| `/admin-access/enrollments/` | `admin_enrollments` | Superuser | Redirect helper to dashboard enrollments tab |
| `/admin-access/users/` | `admin_users` | Superuser | Redirect helper to dashboard users tab |
| `/admin-access/users/<id>/edit/` | `admin_user_edit` | Superuser | Edit user |
| `/admin-access/users/<id>/delete/` | `admin_user_delete` | Superuser POST | Delete user |
| `/admin-access/courses/` | `admin_courses` | Superuser | Redirect helper to dashboard courses tab |
| `/admin-access/courses/<id>/edit/` | `admin_course_edit` | Superuser | Edit course |
| `/admin-access/courses/<id>/delete/` | `admin_course_delete` | Superuser POST | Delete course |
| `/admin-access/courses/<id>/toggle-live/` | `admin_course_toggle_live` | Superuser POST | Course live on/off |
| `/admin-access/sliders/` | `admin_sliders` | Superuser | Redirect helper to dashboard sliders tab |
| `/admin-access/sliders/<id>/edit/` | `admin_slider_edit` | Superuser | Edit slide |
| `/admin-access/sliders/<id>/delete/` | `admin_slider_delete` | Superuser POST | Delete slide |
| `/admin-access/sliders/<id>/toggle-live/` | `admin_slider_toggle_live` | Superuser POST | Slide live on/off |
| `/admin/` | Django admin | Superuser/staff | Model admin |
| `/accounts/*` | allauth | Public | Google/social auth routes |

## 6) Data Models

### 6.1 `Course`

- `title` (unique)
- `slug` (unique)
- `description`
- `duration_weeks`
- `level` (`Beginner`, `Intermediate`, `Advanced`)
- `fee_usd` (decimal amount field)
- `fee_currency` (`USD`, `INR`)
- `is_active`
- `created_at`

Extra property:

- `fee_symbol` returns `$` for USD and rupee symbol for INR

### 6.2 `HomeSlider`

- `title`
- `subtitle`
- `image` (`upload_to="home_slides/"`)
- `button_label`
- `button_url`
- `display_order`
- `is_active`
- `created_at`

### 6.3 `ContactMessage`

- `name`
- `email`
- `company`
- `message`
- `created_at`

### 6.4 `Enrollment`

- `name`
- `email`
- `phone`
- `user` (optional FK to auth user)
- `course` (FK to `Course`, protected)
- `experience` (`Beginner`, `Intermediate`, `Advanced`)
- `notes`
- `created_at`

### 6.5 `Project`

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

## 7) Migration Notes

Applied core migration sequence:

- `0001_initial` - base models
- `0002_enrollment_user` - optional user link on enrollments
- `0003_project` - projects portfolio model
- `0004_course_fee_currency` - `fee_currency` support (`USD`/`INR`)
- `0005_homeslider` - home slider model with image uploads

## 8) Forms

- `ContactForm` - public contact form
- `EnrollmentForm` - enrollment form; only active courses selectable
- `AdminCourseForm` - create/edit courses with slug normalization + uniqueness validation
- `AdminSliderForm` - create/edit slider entries
- `SignUpForm` - registration with unique email check
- `AdminUserCreateForm` - superuser creates users with role flags
- `AdminUserEditForm` - superuser edits users with last-superuser protection

## 9) Admin Dashboard Behavior

Dashboard URL:

- `/admin-access/dashboard/`

Panels:

- `messages` (default)
- `enrollments`
- `sliders`
- `courses`
- `users`

Search query params:

- `messages_q`
- `enrollments_q`
- `sliders_q`
- `courses_q`
- `users_q`

Focused message deep-link:

- `?panel=messages&message=<id>`

POST form handlers by `form_type`:

- `create_course`
- `create_user`
- `create_slider`

Safety controls:

- Superuser guard on all admin-access views
- Cannot delete own currently logged-in user
- Cannot remove/delete last remaining superuser

## 10) Contact Email Notification Flow

When contact form is submitted:

1. Save message to `ContactMessage`.
2. If `CONTACT_RECEIVER_EMAIL` exists, render:
   - `templates/core/emails/contact_notification.txt`
   - `templates/core/emails/contact_notification.html`
3. Send email using `EmailMultiAlternatives`:
   - `to`: `CONTACT_RECEIVER_EMAIL`
   - `reply_to`: sender email from contact form
4. Email contains:
   - Sender details
   - Submitted timestamp
   - Message body
   - Direct dashboard links (all messages and focused single message)

If email fails to send, message is still saved and user receives warning flash message.

## 11) Frontend UX Notes

### 11.1 Home Slider UX

- Edge-to-edge full-width slider section
- Desktop slider height is reduced to `50vh`
- Mobile keeps separate responsive height rules
- Auto smooth slide transitions
- Touch swipe controls for mobile/tablet
- Dot and arrow controls
- Auto-play progress bar
- Reduced motion fallback support

### 11.2 Global Smooth Scroll

- Smooth anchor scrolling is enabled
- JS helper also supports in-page anchor links

### 11.3 Flash Messages (Login/Logout and others)

- Messages are shown as fixed slide-in notification bar
- No page layout space is consumed
- Auto-hide after about 4 seconds

## 12) Static and Media Files

- Static URL: `/static/`
- Static directories: `static/` and `staticfiles/` (collectstatic output)
- Media URL: `/media/`
- Media root: `media/`
- Development media serving is enabled when `DEBUG=True`.

Important:

- Slider image uploads require Pillow.

## 13) Security Controls

Implemented hardening includes:

- Configurable lockout: `MAX_LOGIN_ATTEMPTS`, `LOGIN_LOCKOUT_SECONDS`
- Cookie hardening: `SESSION_COOKIE_HTTPONLY`, `CSRF_COOKIE_HTTPONLY`, `SESSION_COOKIE_SAMESITE`, `CSRF_COOKIE_SAMESITE`
- Browser policy headers: `SECURE_CONTENT_TYPE_NOSNIFF`, `X_FRAME_OPTIONS`, `SECURE_REFERRER_POLICY`, `SECURE_CROSS_ORIGIN_OPENER_POLICY`, `SECURE_CROSS_ORIGIN_RESOURCE_POLICY`
- Production TLS security (`DEBUG=False`): `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, HSTS settings

Operational security notes:

- Never store credentials in repository or documentation.
- Rotate any secret immediately if exposed.
- Frontend code is visible in every browser by design. Keep secrets on backend only.

## 14) Environment Variables

### 14.1 Core App

- `SECRET_KEY`
- `DEBUG`
- `TIME_ZONE`
- `SITE_ID`
- `LOGIN_REDIRECT_URL`
- `LOGOUT_REDIRECT_URL`

### 14.2 Host and CSRF

- `ALLOW_ALL_HOSTS`
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`

### 14.3 Database

- `DATABASE_URL` (preferred in production)
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_HOST`
- `POSTGRES_PORT`

### 14.4 Authentication Security

- `MAX_LOGIN_ATTEMPTS`
- `LOGIN_LOCKOUT_SECONDS`

### 14.5 Google OAuth

- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`

### 14.6 Email

- `EMAIL_BACKEND`
- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_USE_TLS`
- `EMAIL_USE_SSL`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `DEFAULT_FROM_EMAIL`
- `SERVER_EMAIL`
- `CONTACT_RECEIVER_EMAIL`
- `ENROLLMENT_RECEIVER_EMAIL`

### 14.7 POS Installer

- `POS_INSTALLER_PATH`
- `POS_INSTALLER_URL`
- `POS_INSTALLER_FILENAME`

### 14.8 HTTP and Cookie Security

- `SECURE_CONTENT_TYPE_NOSNIFF`
- `X_FRAME_OPTIONS`
- `SECURE_REFERRER_POLICY`
- `SECURE_CROSS_ORIGIN_OPENER_POLICY`
- `SECURE_CROSS_ORIGIN_RESOURCE_POLICY`
- `SECURE_SSL_REDIRECT`
- `SESSION_COOKIE_SECURE`
- `CSRF_COOKIE_SECURE`
- `SESSION_COOKIE_HTTPONLY`
- `CSRF_COOKIE_HTTPONLY`
- `SESSION_COOKIE_SAMESITE`
- `CSRF_COOKIE_SAMESITE`
- `SECURE_HSTS_SECONDS`
- `SECURE_HSTS_INCLUDE_SUBDOMAINS`
- `SECURE_HSTS_PRELOAD`

## 15) Local Setup (Windows PowerShell)

1. Create virtual environment.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Install dependencies.

```powershell
pip install -r requirements.txt
```

3. Create `.env`.

```powershell
Copy-Item .env.example .env
```

4. Apply migrations.

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

7. Run app.

```powershell
python manage.py runserver 0.0.0.0:8000
```

## 16) Google OAuth Setup

In Google Cloud Console:

1. Create OAuth Client ID (Web application).
2. Add JavaScript origins:
- `http://127.0.0.1:8000`
- `http://localhost:8000`
- `https://<your-domain>`
3. Add redirect URIs:
- `http://127.0.0.1:8000/accounts/google/login/callback/`
- `http://localhost:8000/accounts/google/login/callback/`
- `https://<your-domain>/accounts/google/login/callback/`
4. Put client values in `.env`.

## 17) Deployment

### 17.1 Render

- Use `render.yaml`.
- Configure required env vars.
- Set `DEBUG=False`.
- Run `python manage.py createsuperuser` after first deploy.

### 17.2 Docker Compose

```bash
docker compose up --build
```

Entry point performs:

- `migrate`
- `collectstatic`
- optional `seed_courses` when `SEED_COURSES=1`

## 18) Troubleshooting

### 18.1 Google login not showing/enabled

- Confirm `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`.
- Confirm redirect URI and origin configuration.
- Confirm social app config if env-based app config is not used.

### 18.2 Contact email not delivered

- Verify SMTP variables (`EMAIL_HOST`, `EMAIL_PORT`, TLS/SSL, user/password).
- Verify `CONTACT_RECEIVER_EMAIL`.
- Check server logs for SMTP exception.

### 18.3 Installer not downloading

- Confirm user is logged in.
- Confirm `POS_INSTALLER_URL` or valid `POS_INSTALLER_PATH`.
- Confirm local installer file exists and is readable.

### 18.4 Locked out on login

- Wait for configured lockout window.
- Adjust `MAX_LOGIN_ATTEMPTS` and `LOGIN_LOCKOUT_SECONDS` in `.env`.

### 18.5 Media images not loading in development

- Ensure `DEBUG=True`.
- Ensure image files exist under `media/`.
- Ensure migration for `HomeSlider` is applied.

## 19) Useful Commands

```powershell
python manage.py check
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_courses
python manage.py seed_projects
python manage.py collectstatic --noinput
```

## 20) Go-Live Checklist

- Set `DEBUG=False`.
- Set strong `SECRET_KEY`.
- Configure strict `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`.
- Configure HTTPS/TLS and secure cookie settings.
- Configure SMTP + `CONTACT_RECEIVER_EMAIL`.
- Configure Google OAuth production callback.
- Verify admin superuser exists.
- Verify contact email with dashboard deep links.
- Verify slider create/edit/toggle/delete workflow.
- Verify login/register/logout flow and flash notifications.
- Verify `python manage.py check` and `/healthz/`.
