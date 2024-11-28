from django.apps import AppConfig
import sys

class TagsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tags'

    def ready(self):
        # Only start listening if not in migrate command
        if 'migrate' not in sys.argv:
            from .tasks import start_listening
            start_listening()