from django.apps import AppConfig


class AppBadgeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_badge'

    def ready(self):
        import app_badge.signals