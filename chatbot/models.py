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
        # The raw text the user typed into the textarea (user-facing)
        user_query = request.GET.get("q", None)

        # Define the canonical allowed options on the server as (slug, label) pairs.
        # Edit this list to change available checkboxes; template renders labels but submits slugs.
        # Define the canonical allowed options on the server as (slug, label, default_flag) tuples.
        # Defaults are declared here next to the options themselves.
        ALLOWED_CHATBOT_OPTIONS = [
            ('all_about_lib', 'Assume all questions to be about the University of Chicago Library, its services and resources, if applicable.', True),
            ('quotes_and_uncertainty', 'Always either provide a direct quote from the source, or phrase your answer with uncertainty.', True),
            ('follow_up_question', 'Suggest one follow up question.', False),
        ]

        # Helper mapping from slug -> label for validation and canonical labeling
        ALLOWED_CHATBOT_MAP = {slug: label for slug, label, _ in ALLOWED_CHATBOT_OPTIONS}

        # Server-side default selected slugs (will be used if the request doesn't include any options)
        # Compute server-side default slugs from the option declarations
        DEFAULT_SELECTED_SLUGS = [slug for slug, _, default in ALLOWED_CHATBOT_OPTIONS if default]

        # Collect any selected option checkbox values (these should be slugs)
        raw_selected_slugs = request.GET.getlist('options') if hasattr(request, 'GET') else []

        # Detect whether the form was submitted. We use presence of the 'q' param to indicate submission.
        form_submitted = 'q' in request.GET

        # If no options were supplied by the user and the form was NOT submitted, fall back to server-side defaults
        # This prevents re-applying defaults when the user explicitly submitted the form with all boxes unchecked.
        if not raw_selected_slugs and not form_submitted:
            raw_selected_slugs = DEFAULT_SELECTED_SLUGS

        # Validate selected slugs against the allowed map (exact match) to avoid tampering
        validated_slugs = [s for s in raw_selected_slugs if s in ALLOWED_CHATBOT_MAP]

        # Map validated slugs to canonical labels for assembling the prompt
        validated_labels = [ALLOWED_CHATBOT_MAP[s] for s in validated_slugs]

        # Build a prefix from validated labels if any are present
        sent_query = user_query
        if validated_labels:
            # Join labels with '; ' and add two newlines as a separator
            prefix = '; '.join([lbl.strip() for lbl in validated_labels if lbl and lbl.strip()]) + "\n\n"
            # If the user's query already starts with the same prefix, assume they already included it
            if user_query:
                if not user_query.startswith(prefix):
                    sent_query = prefix + user_query
            else:
                sent_query = prefix

        result = None

        if sent_query:
            try:
                index = SelectedPagesVectorIndex()
                query_result = index.query(sent_query)

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
        # Expose allowed options (slug,label pairs) to the template so checkboxes can be rendered server-side
        context["allowed_options"] = ALLOWED_CHATBOT_OPTIONS
        # Pass back which slugs were selected so the template can pre-check them
        context["selected_option_slugs"] = validated_slugs
        # Pass whether the form was submitted so the template can decide whether to show defaults or the user's choices
        context["form_submitted"] = form_submitted
        # Provide the user-facing query separately from the query actually sent to the index
        context["query"] = user_query
        # context["sent_query"] = sent_query
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
