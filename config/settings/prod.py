from .base import *  # noqa

DEBUG = False
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["tbss.example.com"])  # set via env

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True

EMAIL_BACKEND = "anymail.backends.smtp.EmailBackend"

# Redis cache optional via env
if env("REDIS_URL", default=None):
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": env("REDIS_URL"),
            "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        }
    }
