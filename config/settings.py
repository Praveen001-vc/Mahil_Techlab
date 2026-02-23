from pathlib import Path
import os

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent


def load_env_file(path):
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        os.environ.setdefault(key, value)


load_env_file(BASE_DIR / ".env")

def env_bool(name, default=False):
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def env_list(name, default=""):
    return [value.strip() for value in os.getenv(name, default).split(",") if value.strip()]


SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-change-this-in-production")
DEBUG = env_bool("DEBUG", True)

DEFAULT_ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "mahil-techlab.onrender.com",
    "mahil-techlab-web.onrender.com",
]
DEFAULT_CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "https://mahil-techlab.onrender.com",
    "https://mahil-techlab-web.onrender.com",
]

ALLOW_ALL_HOSTS = env_bool("ALLOW_ALL_HOSTS", False)
if ALLOW_ALL_HOSTS:
    ALLOWED_HOSTS = ["*"]
else:
    configured_allowed_hosts = env_list("ALLOWED_HOSTS", "")
    ALLOWED_HOSTS = list(dict.fromkeys(DEFAULT_ALLOWED_HOSTS + configured_allowed_hosts))
configured_csrf_trusted_origins = env_list("CSRF_TRUSTED_ORIGINS", "")
CSRF_TRUSTED_ORIGINS = list(
    dict.fromkeys(DEFAULT_CSRF_TRUSTED_ORIGINS + configured_csrf_trusted_origins)
)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

database_url = os.getenv("DATABASE_URL", "").strip()
if database_url:
    DATABASES = {
        "default": dj_database_url.parse(
            database_url,
            conn_max_age=600,
            ssl_require=not DEBUG,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRES_DB", "mahil_techlab"),
            "USER": os.getenv("POSTGRES_USER", "postgres"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", "postgres"),
            "HOST": os.getenv("POSTGRES_HOST", "127.0.0.1"),
            "PORT": os.getenv("POSTGRES_PORT", "5432"),
        }
    }

if DEBUG:
    # Dev mode: allow simple passwords (including same as username) for easy local testing.
    AUTH_PASSWORD_VALIDATORS = []
else:
    AUTH_PASSWORD_VALIDATORS = [
        {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
        {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
        {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
        {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
    ]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

SITE_ID = int(os.getenv("SITE_ID", "1"))

LOGIN_REDIRECT_URL = os.getenv("LOGIN_REDIRECT_URL", "/")
LOGOUT_REDIRECT_URL = os.getenv("LOGOUT_REDIRECT_URL", "/")

SOCIALACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
    }
}

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "").strip()
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()

if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
    SOCIALACCOUNT_PROVIDERS["google"]["APP"] = {
        "client_id": GOOGLE_CLIENT_ID,
        "secret": GOOGLE_CLIENT_SECRET,
        "key": "",
    }

DEFAULT_POS_INSTALLER_PATH = (
    Path.home()
    / "Documents"
    / "GitHub"
    / "mahilmart-pos"
    / "installer"
    / "output"
    / "MahilMartPOS-Setup.exe"
)
POS_INSTALLER_PATH = (os.getenv("POS_INSTALLER_PATH") or str(DEFAULT_POS_INSTALLER_PATH)).strip()
DEFAULT_POS_INSTALLER_URL = (
    "https://raw.githubusercontent.com/Praveen001-vc/"
    "mahilmart-pos-Version01/main/installer/output/MahilMartPOS-Setup.exe"
)
POS_INSTALLER_URL = (os.getenv("POS_INSTALLER_URL") or DEFAULT_POS_INSTALLER_URL).strip()
POS_INSTALLER_FILENAME = (os.getenv("POS_INSTALLER_FILENAME") or "MahilMartPOS-Setup.exe").strip()

LANGUAGE_CODE = "en-us"
TIME_ZONE = os.getenv("TIME_ZONE", "UTC")
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", True)
    SESSION_COOKIE_SECURE = env_bool("SESSION_COOKIE_SECURE", True)
    CSRF_COOKIE_SECURE = env_bool("CSRF_COOKIE_SECURE", True)
    SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "31536000"))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", True)
    SECURE_HSTS_PRELOAD = env_bool("SECURE_HSTS_PRELOAD", True)
else:
    SECURE_SSL_REDIRECT = False

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
