from pathlib import Path
import os
from urllib.parse import urlparse, urlunparse

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent


def _normalize_render_database_url(url: str) -> str:
    """Prefer external URL; upgrade internal Render hostnames when needed."""
    external = os.environ.get("DATABASE_EXTERNAL_URL")
    if external:
        return external
    if not url or "sqlite" in url:
        return url

    parsed = urlparse(url)
    host = parsed.hostname
    if host and host.startswith("dpg-") and "." not in host:
        region = os.environ.get("RENDER_DB_REGION", "oregon")
        new_host = f"{host}.{region}-postgres.render.com"
        auth = ""
        if parsed.username:
            auth = parsed.username
            if parsed.password:
                auth = f"{auth}:{parsed.password}"
            auth = f"{auth}@"
        port = f":{parsed.port}" if parsed.port else ""
        new_netloc = f"{auth}{new_host}{port}"
        return urlunparse(parsed._replace(netloc=new_netloc))
    return url

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-dev-only-change-in-production",
)

DEBUG = os.environ.get(
    "DEBUG",
    "false" if os.environ.get("RENDER") else "true",
).lower() in ("1", "true", "yes")

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1,web").split(",")
    if host.strip()
]

RENDER_HOST = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if RENDER_HOST:
    ALLOWED_HOSTS.append(RENDER_HOST)

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]
if RENDER_HOST:
    CSRF_TRUSTED_ORIGINS.append(f"https://{RENDER_HOST}")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "data_manager",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

DATABASE_URL = _normalize_render_database_url(os.environ.get("DATABASE_URL", ""))
if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=True,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

PROJECT_ROOT = Path(os.environ.get("PROJECT_ROOT", BASE_DIR.parent))
DATASETS_DIR = Path(os.environ.get("DATASETS_DIR", BASE_DIR / "datasets"))
DATASETS_DIR.mkdir(parents=True, exist_ok=True)

AUTO_PIPELINE = os.environ.get("AUTO_PIPELINE", "true").lower() in ("1", "true", "yes")
API_RELOAD_URL = os.environ.get(
    "API_RELOAD_URL",
    "http://127.0.0.1:8000/reload-models",
)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = os.environ.get("SECURE_SSL_REDIRECT", "true").lower() in (
        "1",
        "true",
        "yes",
    )
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
