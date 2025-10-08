from django.apps import AppConfig


class DynamicDjangoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'DynamicDjango'
