from django.apps import AppConfig

from tags.tasks import start_listening


class TagsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tags'
    def ready(self):

        start_listening()
