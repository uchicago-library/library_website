from django.apps import AppConfig


class VectorIndexConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "vector_index"

    def ready(self):
        from wagtail_vector_index.storage import registry

        from .indexes import SelectedPagesVectorIndex

        registry.register_index(SelectedPagesVectorIndex())
