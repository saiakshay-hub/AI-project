from django.apps import AppConfig


class InternalAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'internal_app'
