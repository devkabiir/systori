from systori.settings.common import *
import os

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SERVER_NAME = "systori.com"
SESSION_COOKIE_DOMAIN = "." + SERVER_NAME
ALLOWED_HOSTS = ["." + SERVER_NAME]

DATABASES["default"].update(
    {"HOST": "db", "NAME": "systori_production", "USER": "postgres"}
)

idx = INSTALLED_APPS.index("django.contrib.staticfiles")
INSTALLED_APPS = (
    INSTALLED_APPS[:idx] + ("whitenoise.runserver_nostatic",) + INSTALLED_APPS[idx:]
)

INSTALLED_APPS += ("raven.contrib.django.raven_compat",)

RAVEN_CONFIG = {
    "dsn": "https://11c0341ce6d74de7968932986090227d:406344d994aa4524818e99d45cf8d44b@sentry.systorigin.de/1"
}
