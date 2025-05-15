from lib_news.models import LibNewsPage
from public.models import StandardPage
from wagtail_vector_index.storage.base import Document, VectorIndex
from wagtail_vector_index.storage.models import (
    EmbeddableFieldsDocumentConverter,
    EmbeddableFieldsVectorIndexMixin,
)
from wagtail_vector_index.storage.pgvector import PgvectorIndexMixin


class MultiModelDocumentConverter(EmbeddableFieldsDocumentConverter):
    def bulk_from_documents(self, documents):
        # Convert to list for debugging/multiple iteration
        docs = list(documents)

        # Get object IDs as integers
        object_ids = [
            int(doc.metadata.get("object_id"))
            for doc in docs
            if doc.metadata.get("object_id")
        ]

        # Fetch pages with one query
        pages = {}
        for p in self.base_model.objects.filter(pk__in=object_ids):
            key = (p.pk, getattr(p, 'content_type_id', None))
            pages[key] = p

        # Yield pages that match documents
        for doc in docs:
            if "object_id" in doc.metadata and doc.metadata["object_id"]:
                object_id = int(doc.metadata["object_id"])
                content_type_id = (
                    int(doc.metadata["content_type_id"])
                    if doc.metadata.get("content_type_id")
                    else None
                )
                lookup_key = (object_id, content_type_id)
                if lookup_key in pages:
                    page = pages[lookup_key]
                    # Get specific model instance, not just Page
                    specific_page = page.specific
                    yield specific_page

    def to_document(self, obj, embedding_backend):
        # Metadata with information needed for retrieval
        meta = {
            "model": obj._meta.label,
            "pk": obj.pk,
            "object_id": obj.pk,
            "content_type_id": (
                obj.content_type_id if hasattr(obj, 'content_type_id') else None
            ),
            # Include page content for context
            "content": self._extract_text(obj),
        }

        # Extract text for embedding
        text = " ".join(
            [str(getattr(obj, field.field_name)) for field in obj.embedding_fields]
        )

        # Generate vector embedding and ensure it's flat (1D)
        vector_result = list(embedding_backend.embed(text))

        # Check if we need to flatten (if it's a nested list)
        if len(vector_result) == 1 and isinstance(vector_result[0], (list, tuple)):
            vector = vector_result[0]  # Take the first (and only) inner list
        else:
            vector = vector_result

        # Get embedding_pk if available
        embedding_pk = None
        embeddings_manager = getattr(obj, 'embeddings', None)
        if embeddings_manager is not None:
            first_embedding = embeddings_manager.first()
            if first_embedding is not None:
                embedding_pk = first_embedding.pk

        return Document(
            vector=vector,
            metadata=meta,
            embedding_pk=embedding_pk,
        )

    def _extract_text(self, obj):
        """Extract rich text content from the page"""
        # This is a helper method to extract all relevant text from different page types
        # You may need to customize this based on your page models' structure
        content = []

        # Add title
        content.append(str(obj.title))

        # Extract from common rich text fields
        for field_name in ['body', 'content', 'description', 'intro']:
            if hasattr(obj, field_name):
                field_value = getattr(obj, field_name)
                if field_value:
                    content.append(str(field_value))

        return "\n".join(content)


class SelectedPagesVectorIndex(
    EmbeddableFieldsVectorIndexMixin, PgvectorIndexMixin, VectorIndex
):
    # Use issubclass to filter models implementing a specific mixin
    # This approach can be adapted if you have a custom mixin
    querysets = [
        StandardPage.objects.all(),
        LibNewsPage.objects.all(),
    ]

    def get_converter_class(self):
        return MultiModelDocumentConverter

    def get_converter(self, model_class=None):
        from wagtail.models import Page

        return self.get_converter_class()(Page)

    def get_documents(self):
        from library_website.settings import WAGTAIL_VECTOR_INDEX
        from wagtail_vector_index.ai_utils.backends import get_embedding_backend

        backend_dict = WAGTAIL_VECTOR_INDEX["EMBEDDING_BACKENDS"]["default"]
        backend_id = "default"
        embedding_backend = get_embedding_backend(
            backend_dict=backend_dict, backend_id=backend_id
        )
        converter = self.get_converter()

        # Only process objects that have valid embeddings
        for queryset in self.querysets:
            # Filter to only include objects with embeddings
            objects_with_embeddings = []
            for obj in queryset:
                embeddings_manager = getattr(obj, 'embeddings', None)
                if embeddings_manager is not None and embeddings_manager.exists():
                    objects_with_embeddings.append(obj)

            # Log how many objects have embeddings
            print(
                f"Found {len(objects_with_embeddings)} objects with embeddings out of {queryset.count()} total"
            )

            # Only process objects that have valid embeddings
            for obj in objects_with_embeddings:
                yield converter.to_document(obj, embedding_backend)
