from systori.settings.common import *

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SERVER_NAME = "sandbox.systori.com"
SESSION_COOKIE_DOMAIN = "." + SERVER_NAME
ALLOWED_HOSTS = ["." + SERVER_NAME]

idx = INSTALLED_APPS.index("django.contrib.staticfiles")
INSTALLED_APPS = (
    INSTALLED_APPS[:idx] + ("whitenoise.runserver_nostatic",) + INSTALLED_APPS[idx:]
)

STATICFILES_DIRS += (("dart/src", "systori/dart/web"),)

DATABASES["default"].update(
    {"HOST": "db", "NAME": "systori_sandbox", "USER": "postgres"}
)

INSTALLED_APPS += ("raven.contrib.django.raven_compat",)

RAVEN_CONFIG = {
    "dsn": "https://11c0341ce6d74de7968932986090227d:406344d994aa4524818e99d45cf8d44b@sentry.systori.io/1"
}
