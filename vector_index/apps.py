from django.apps import AppConfig


class VectorIndexConfig(AppConfig):
    name = "library_website.vector_index"

    def ready(self):
        from wagtail_vector_index.index import registry

        from .indexes import SelectedPagesVectorIndex

        registry.register()(SelectedPagesVectorIndex)
