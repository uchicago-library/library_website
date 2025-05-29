from base.models import PublicBasePage
from django.shortcuts import render
from vector_index.indexes import SelectedPagesVectorIndex
from wagtail.models import Page


class ChatbotPage(PublicBasePage):

    content_panels = Page.content_panels + PublicBasePage.content_panels + []

    # Template path
    template = "chatbot/chatbot_page.html"

    # Override serve to handle the query and render the template
    def serve(self, request, *args, **kwargs):
        query = request.GET.get("q", None)
        result = None

        if query:
            try:
                index = SelectedPagesVectorIndex()
                query_result = index.query(query)

                # QueryResponse is an object, not a dictionary
                # Access its attributes directly
                if query_result:
                    result = {
                        'answer': (
                            query_result.response
                            if hasattr(query_result, 'response')
                            else "I couldn't find an answer to that."
                        ),
                        'sources': (
                            query_result.sources
                            if hasattr(query_result, 'sources')
                            else []
                        ),
                    }
                else:
                    # Handle case where no result is returned
                    result = {
                        'answer': "I couldn't find an answer to that.",
                        'sources': [],
                    }

            except Exception as e:
                # Handle potential errors during query (e.g., index not ready, API errors)
                result = {'answer': f"Error querying index: {str(e)}", 'sources': []}

        context = self.get_context(request)
        context["query"] = query
        context["result"] = result

        # Check if this is an htmx request (using django-htmx middleware)
        if request.htmx:
            # If it's an htmx request, just render the partial template
            return render(request, "chatbot/results_partial.html", context)
        # For regular requests, render the full page
        return render(request, self.template, context)

    # Optional: Limit where this page can be created
    parent_page_types = [
        'home.HomePage',
        'public.StandardPage',
    ]
    # subpage_types = []
