from .base import *  # noqa

DEBUG = False
ALLOWED_HOSTS = ["*"]
EMAIL_BACKEND = "anymail.backends.console.EmailBackend"

# Simple cache for dev
CACHES["default"]["BACKEND"] = "django.core.cache.backends.locmem.LocMemCache"
