import json
import os
import re

import html2text
import requests
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from base.wagtail_hooks import get_required_groups, has_permission
from cgimail_editor.models import CGIMailFormEditorPage
from intranethome.models import IntranetHomePage


def check_loop_permission(request):
    """
    Check if the user has permission to access the intranet.
    Returns None if permitted, or a JsonResponse with 403 if not.
    """
    try:
        # Find the intranet home page (should be Loop root)
        intranet_home = IntranetHomePage.objects.live().first()
        if intranet_home:
            if not has_permission(request.user, get_required_groups(intranet_home)):
                return JsonResponse(
                    {"error": "Unauthorized - intranet access required"},
                    status=403,
                )
    except Exception:
        # If intranet doesn't exist, allow access (dev environment)
        pass
    return None


@require_http_methods(["GET"])
def fetch_surrogates(request):
    """
    Fetch available CGIMail surrogates from API.
    Falls back to CGI_SURROGATES_FALLBACK setting if API fails and a fallback is configured.
    If no fallback is configured, API failures return errors.
    """
    permission_error = check_loop_permission(request)
    if permission_error:
        return permission_error

    api_url = getattr(settings, "CGI_SURROGATES_API", "")
    fallback_list = getattr(settings, "CGI_SURROGATES_FALLBACK", [])

    # Try to fetch from API if configured
    if api_url:
        try:
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return JsonResponse(
                {
                    "surrogates": data.get("surrogates", []),
                    "fallback": False,
                }
            )
        except Exception as e:
            # API call failed - use fallback if available, otherwise error
            if fallback_list:
                return JsonResponse(
                    {
                        "surrogates": fallback_list,
                        "fallback": True,
                        "api_error": str(e),
                    }
                )
            # No fallback available - return error
            return JsonResponse(
                {"error": f"Surrogate API unavailable: {str(e)}"},
                status=503,
            )

    # No API configured - use fallback if available
    if fallback_list:
        return JsonResponse(
            {
                "surrogates": fallback_list,
                "fallback": True,
            }
        )

    # Neither API nor fallback configured - return error
    return JsonResponse(
        {"error": "No surrogate API or fallback configured"},
        status=500,
    )


@require_http_methods(["POST"])
def fetch_documentation(request):
    """
    Fetch and convert documentation sources to Markdown.
    Returns concatenated markdown for AI context.
    Supports both external URLs (any website) and internal Wagtail pages.
    """
    permission_error = check_loop_permission(request)
    if permission_error:
        return permission_error

    try:
        editor_page = CGIMailFormEditorPage.objects.first()
        if not editor_page:
            return JsonResponse({"error": "Editor page not configured"}, status=404)

        docs = []
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = True
        h.body_width = 0  # Don't wrap lines

        for source in editor_page.documentation_sources.all():
            doc_entry = {"source": source.description}
            try:
                if source.url:
                    resp = requests.get(
                        source.url,
                        timeout=15,
                        headers={
                            "User-Agent": "Mozilla/5.0 (compatible; UChicagoLibrary/1.0)"
                        },
                    )
                    resp.raise_for_status()
                    markdown = h.handle(resp.text)
                    doc_entry["content"] = markdown
                elif source.internal_page:
                    page = source.internal_page.specific
                    content = _extract_page_content(page)
                    markdown = h.handle(content)
                    doc_entry["content"] = markdown
                else:
                    doc_entry["error"] = "No URL or page specified"
            except Exception as e:
                doc_entry["error"] = str(e)

            docs.append(doc_entry)

        return JsonResponse({"documentation": docs})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def _extract_page_content(page):
    """Extract HTML content from various Wagtail page types."""
    content_parts = []

    # Add title
    if hasattr(page, "title"):
        content_parts.append(f"<h1>{page.title}</h1>")

    # Try to get body content (StreamField or RichTextField)
    if hasattr(page, "body"):
        body = page.body
        if hasattr(body, "__html__"):
            content_parts.append(body.__html__())
        elif hasattr(body, "render_as_block"):
            content_parts.append(str(body.render_as_block()))
        else:
            content_parts.append(str(body))

    # Try intro field
    if hasattr(page, "intro") and page.intro:
        intro = page.intro
        if hasattr(intro, "__html__"):
            content_parts.append(intro.__html__())
        else:
            content_parts.append(str(intro))

    return "\n".join(content_parts)


@require_http_methods(["POST"])
def generate_form_json(request):
    """
    Proxy to OpenAI API for generating CGIMail form JSON.
    Builds prompt with documentation context and schema.
    """
    permission_error = check_loop_permission(request)
    if permission_error:
        return permission_error

    api_key = getattr(settings, "OPENAI_CGIMAIL_KEY", "")
    if not api_key:
        return JsonResponse(
            {"error": "OpenAI API key not configured"},
            status=500,
        )

    try:
        data = json.loads(request.body)

        mode = data.get("mode", "create")
        surrogate = data.get("surrogate", "")
        subject = data.get("subject", "")
        description = data.get("description", "")
        existing_json = data.get("existing_json")
        documentation = data.get("documentation", [])
        system_prompt = data.get("system_prompt", "")

        default_model = CGIMailFormEditorPage._meta.get_field("ai_model").default
        model = data.get("model", default_model)

        # Read schema for AI context
        schema_content = _read_schema()

        # Build prompt
        prompt = _build_prompt(
            mode=mode,
            surrogate=surrogate,
            subject=subject,
            description=description,
            existing_json=existing_json,
            documentation=documentation,
            schema_content=schema_content,
        )

        # Call OpenAI API
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        # o1 and o3 models don't support system messages or custom temperature
        is_reasoning_model = model.startswith("o1") or model.startswith("o3")

        if is_reasoning_model:
            # For o1/o3: combine system prompt into user message, use default temperature
            combined_prompt = f"{system_prompt}\n\n---\n\n{prompt}"
            payload = {
                "model": model,
                "messages": [
                    {"role": "user", "content": combined_prompt},
                ],
            }
        else:
            # For GPT models: use system message and custom temperature
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.2,
            }

        api_endpoint = getattr(
            settings,
            "OPENAI_API_ENDPOINT",
            "https://api.openai.com/v1/chat/completions",
        )
        response = requests.post(
            api_endpoint,
            headers=headers,
            json=payload,
            timeout=60,
        )
        response.raise_for_status()

        result = response.json()
        generated_text = result["choices"][0]["message"]["content"]

        # Extract JSON from response (may have markdown code blocks)
        generated_json = _extract_json(generated_text)

        return JsonResponse(
            {
                "success": True,
                "json": generated_json,
                "raw_response": generated_text,
            }
        )

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON in request"}, status=400)
    except requests.exceptions.Timeout:
        return JsonResponse(
            {"error": "OpenAI API request timed out"},
            status=504,
        )
    except requests.exceptions.RequestException as e:
        return JsonResponse(
            {"error": f"OpenAI API error: {str(e)}"},
            status=502,
        )
    except Exception as e:
        return JsonResponse(
            {"success": False, "error": str(e)},
            status=500,
        )


def _read_schema():
    """Read the CGIMailFormSchema.js file content."""
    schema_path = os.path.join(
        settings.BASE_DIR,
        "base",
        "static",
        "base",
        "js",
        "CGIMailFormSchema.js",
    )
    try:
        with open(schema_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return "// Schema file not found"


def _build_prompt(
    mode, surrogate, subject, description, existing_json, documentation, schema_content
):
    """Build the user prompt for OpenAI."""
    prompt_parts = []

    # Add documentation context
    if documentation:
        prompt_parts.append("# Documentation Context")
        for doc in documentation:
            if "error" not in doc and "content" in doc:
                prompt_parts.append(f"## {doc.get('source', 'Unknown')}")
                # Truncate very long docs to avoid token limits
                content = doc["content"]
                if len(content) > 5000:
                    content = content[:5000] + "\n... (truncated)"
                prompt_parts.append(content)
        prompt_parts.append("\n---\n")

    # Add schema
    prompt_parts.append("# CGIMail Form Schema (you MUST follow this exactly)")
    prompt_parts.append(f"```javascript\n{schema_content}\n```\n")

    # Add task
    if mode == "create":
        prompt_parts.append("# Task: Create New Form")
        prompt_parts.append(f"Recipient (surrogate email): {surrogate}")
        prompt_parts.append(f"Subject line for emails: {subject}")
        prompt_parts.append(f"\nForm requirements:\n{description}")
        prompt_parts.append(
            "\nGenerate complete valid JSON following the schema. "
            "Output ONLY the JSON object, no explanations."
        )
    else:  # edit mode
        prompt_parts.append("# Task: Edit Existing Form")
        prompt_parts.append(f"Current JSON:\n```json\n{existing_json}\n```")
        prompt_parts.append(f"\nRequested changes:\n{description}")
        prompt_parts.append(
            "\nGenerate the modified JSON. Output ONLY the JSON object, no explanations."
        )

    return "\n".join(prompt_parts)


def _extract_json(text):
    """Extract JSON from AI response (may be wrapped in markdown)."""
    # Try to find JSON in code blocks
    code_block_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if code_block_match:
        return code_block_match.group(1)

    # Try to find raw JSON (starts with { and ends with })
    json_match = re.search(r"(\{.*\})", text, re.DOTALL)
    if json_match:
        return json_match.group(1)

    return text
