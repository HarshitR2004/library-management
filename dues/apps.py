from django.apps import AppConfig


class DuesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dues'

    def ready(self):
        import dues.signals 
