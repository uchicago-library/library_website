import json
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import Client, TestCase, override_settings
from wagtail.models import Page
from wagtail.test.utils import WagtailPageTestCase

from cgimail_editor.models import CGIMailFormEditorPage, DocumentationSource
from cgimail_editor.views import _build_prompt, _extract_json, _extract_page_content
from staff.models import StaffPage

User = get_user_model()


class DocumentationSourceTests(TestCase):
    """Test DocumentationSource model validation."""

    @classmethod
    def setUpTestData(cls):
        # Create a StaffPage for page_maintainer and editor fields
        root = Page.objects.get(id=1)
        cls.staff = StaffPage(
            title="Test Staff",
            cnetid="teststaff",
            slug="test-staff",
        )
        root.add_child(instance=cls.staff)

        # Create a CGIMailFormEditorPage to attach sources to
        cls.editor_page = CGIMailFormEditorPage(
            title="Test Editor",
            slug="test-editor",
            page_maintainer=cls.staff,
            editor=cls.staff,
        )
        root.add_child(instance=cls.editor_page)

    def test_requires_either_url_or_internal_page(self):
        """Should raise ValidationError if neither URL nor internal page provided."""
        source = DocumentationSource(
            page=self.editor_page,
            description="Test source",
        )
        with self.assertRaises(ValidationError) as cm:
            source.clean()
        self.assertIn("Either URL or Internal Page must be provided", str(cm.exception))

    def test_rejects_both_url_and_internal_page(self):
        """Should raise ValidationError if both URL and internal page provided."""
        other_page = StaffPage(
            title="Other Staff",
            slug="other-staff",
            cnetid="otherstaff",
        )
        Page.objects.get(id=1).add_child(instance=other_page)

        source = DocumentationSource(
            page=self.editor_page,
            url="https://example.com",
            internal_page=other_page,
            description="Test source",
        )
        with self.assertRaises(ValidationError) as cm:
            source.clean()
        self.assertIn(
            "Provide either URL or Internal Page, not both", str(cm.exception)
        )

    def test_accepts_url_only(self):
        """Should accept source with only URL."""
        source = DocumentationSource(
            page=self.editor_page,
            url="https://example.com",
            description="Test source",
        )
        source.clean()  # Should not raise

    def test_accepts_internal_page_only(self):
        """Should accept source with only internal page."""
        other_page = StaffPage(
            title="Other Staff 2",
            slug="other-staff-2",
            cnetid="otherstaff2",
        )
        Page.objects.get(id=1).add_child(instance=other_page)

        source = DocumentationSource(
            page=self.editor_page,
            internal_page=other_page,
            description="Test source",
        )
        source.clean()  # Should not raise

    def test_str_returns_description(self):
        """__str__ should return description if available."""
        source = DocumentationSource(
            page=self.editor_page,
            url="https://example.com",
            description="My description",
        )
        self.assertEqual(str(source), "My description")


class CGIMailFormEditorPageTests(WagtailPageTestCase):
    """Test CGIMailFormEditorPage model."""

    @classmethod
    def setUpTestData(cls):
        # Create a StaffPage for page_maintainer and editor fields
        root = Page.objects.get(id=1)
        cls.staff = StaffPage(
            title="Test Staff",
            cnetid="teststaff2",
            slug="test-staff-2",
        )
        root.add_child(instance=cls.staff)

        # Create an IntranetHomePage as valid parent for CGIMailFormEditorPage
        from intranethome.models import IntranetHomePage

        cls.intranet_home = IntranetHomePage(
            title="Intranet Home",
            slug="intranet-home",
            page_maintainer=cls.staff,
            editor=cls.staff,
        )
        root.add_child(instance=cls.intranet_home)

    def test_singleton_enforcement(self):
        """Should only allow one instance of CGIMailFormEditorPage."""
        # Before creating any instances, should be able to create
        self.assertTrue(CGIMailFormEditorPage.can_create_at(self.intranet_home))

        # Create first instance
        page1 = CGIMailFormEditorPage(
            title="Editor 1",
            slug="editor-1",
            page_maintainer=self.staff,
            editor=self.staff,
        )
        self.intranet_home.add_child(instance=page1)

        # After creating one instance, should not be able to create another
        self.assertFalse(CGIMailFormEditorPage.can_create_at(self.intranet_home))

    def test_get_context_includes_api_urls(self):
        """get_context should include API endpoint URLs."""
        page = CGIMailFormEditorPage(
            title="Editor",
            slug="editor",
            page_maintainer=self.staff,
            editor=self.staff,
        )
        self.intranet_home.add_child(instance=page)

        request = Mock()
        context = page.get_context(request)

        self.assertEqual(
            context["surrogate_api_url"], "/cgimail-editor/api/surrogates/"
        )
        self.assertEqual(context["generate_api_url"], "/cgimail-editor/api/generate/")
        self.assertEqual(
            context["fetch_docs_api_url"], "/cgimail-editor/api/fetch-docs/"
        )

    def test_get_context_includes_ai_configuration(self):
        """get_context should pass AI model and prompts to template."""
        page = CGIMailFormEditorPage(
            title="Editor",
            slug="editor-2",
            ai_model="gpt-4o",
            system_prompt="Test prompt",
            template_description="Test template",
            page_maintainer=self.staff,
            editor=self.staff,
        )
        self.intranet_home.add_child(instance=page)

        request = Mock()
        context = page.get_context(request)

        self.assertEqual(context["ai_model"], "gpt-4o")
        self.assertEqual(context["system_prompt"], "Test prompt")
        self.assertEqual(context["template_description"], "Test template")


class PermissionTests(TestCase):
    """Test Loop permission checks."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="testuser", password="testpass")

    def setUp(self):
        self.client = Client()

    @patch("cgimail_editor.views.get_required_groups")
    @patch("cgimail_editor.views.IntranetHomePage.objects.live")
    @patch("cgimail_editor.views.has_permission")
    def test_check_loop_permission_allows_authorized_users(
        self, mock_has_permission, mock_live, mock_get_groups
    ):
        """Authorized users should get None (allowed)."""
        from cgimail_editor.views import check_loop_permission

        mock_has_permission.return_value = True
        mock_get_groups.return_value = []
        mock_intranet = Mock()
        mock_live.return_value.first.return_value = mock_intranet

        request = Mock()
        request.user = self.user

        result = check_loop_permission(request)
        self.assertIsNone(result)

    @patch("cgimail_editor.views.get_required_groups")
    @patch("cgimail_editor.views.IntranetHomePage.objects.live")
    @patch("cgimail_editor.views.has_permission")
    def test_check_loop_permission_blocks_unauthorized_users(
        self, mock_has_permission, mock_live, mock_get_groups
    ):
        """Unauthorized users should get 403 JsonResponse."""
        from cgimail_editor.views import check_loop_permission

        mock_has_permission.return_value = False
        mock_get_groups.return_value = []
        mock_intranet = Mock()
        mock_live.return_value.first.return_value = mock_intranet

        request = Mock()
        request.user = self.user

        result = check_loop_permission(request)
        self.assertEqual(result.status_code, 403)
        data = json.loads(result.content)
        self.assertIn("Unauthorized", data["error"])


@override_settings(
    CGI_SURROGATES_API="",
    CGI_SURROGATES_FALLBACK=["askus", "circ", "ill"],
)
class FetchSurrogatesTests(TestCase):
    """Test fetch_surrogates view."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="testuser", password="testpass", is_staff=True
        )

    def setUp(self):
        self.client = Client()

    @patch("cgimail_editor.views.check_loop_permission")
    def test_uses_fallback_when_no_api_configured(self, mock_permission):
        """Should return fallback surrogates when API not configured."""
        mock_permission.return_value = None
        self.client.force_login(self.user)

        response = self.client.get("/cgimail-editor/api/surrogates/")
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEqual(data["surrogates"], ["askus", "circ", "ill"])
        self.assertTrue(data["fallback"])

    @patch("cgimail_editor.views.check_loop_permission")
    def test_returns_403_when_permission_denied(self, mock_permission):
        """Should return 403 when user lacks Loop access."""
        from django.http import JsonResponse

        mock_permission.return_value = JsonResponse(
            {"error": "Unauthorized"}, status=403
        )

        response = self.client.get("/cgimail-editor/api/surrogates/")
        self.assertEqual(response.status_code, 403)
        mock_permission.assert_called_once()


class FetchDocumentationTests(TestCase):
    """Test fetch_documentation view."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="testuser", password="testpass", is_staff=True
        )
        root = Page.objects.get(id=1)
        cls.staff = StaffPage(
            title="Test Staff",
            cnetid="teststaff3",
            slug="test-staff-3",
        )
        root.add_child(instance=cls.staff)

    def setUp(self):
        self.client = Client()
        # Create editor_page per test since one test deletes it
        root = Page.objects.get(id=1)
        self.editor_page = CGIMailFormEditorPage(
            title="Editor",
            slug="editor",
            page_maintainer=self.staff,
            editor=self.staff,
        )
        root.add_child(instance=self.editor_page)

    @patch("cgimail_editor.views.check_loop_permission")
    def test_returns_404_when_no_editor_page(self, mock_permission):
        """Should return 404 when editor page doesn't exist."""
        mock_permission.return_value = None
        self.client.force_login(self.user)

        # Delete the editor page
        self.editor_page.delete()

        response = self.client.post(
            "/cgimail-editor/api/fetch-docs/",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    @patch("cgimail_editor.views.check_loop_permission")
    @patch("cgimail_editor.views.requests.get")
    def test_fetches_external_url(self, mock_get, mock_permission):
        """Should fetch and convert external URLs to markdown."""
        mock_permission.return_value = None
        self.client.force_login(self.user)

        # Add documentation source with URL
        DocumentationSource.objects.create(
            page=self.editor_page,
            url="https://example.com",
            description="Test docs",
        )

        mock_response = Mock()
        mock_response.text = "<h1>Test</h1><p>Content</p>"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        response = self.client.post(
            "/cgimail-editor/api/fetch-docs/",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEqual(len(data["documentation"]), 1)
        self.assertEqual(data["documentation"][0]["source"], "Test docs")

        # Verify HTML was converted to markdown (not raw HTML)
        content = data["documentation"][0]["content"]
        self.assertIn("Test", content)
        self.assertIn("Content", content)
        self.assertNotIn("<h1>", content)
        self.assertNotIn("<p>", content)


class GenerateFormJSONTests(TestCase):
    """Test generate_form_json view."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="testuser", password="testpass", is_staff=True
        )

    def setUp(self):
        self.client = Client()

    @override_settings(OPENAI_CGIMAIL_KEY="")
    @patch("cgimail_editor.views.check_loop_permission")
    def test_returns_error_when_no_api_key(self, mock_permission):
        """Should return 500 when OpenAI API key not configured."""
        mock_permission.return_value = None
        self.client.force_login(self.user)

        response = self.client.post(
            "/cgimail-editor/api/generate/",
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.content)
        self.assertIn("API key not configured", data["error"])

    @override_settings(OPENAI_CGIMAIL_KEY="test-key")
    @patch("cgimail_editor.views.check_loop_permission")
    @patch("cgimail_editor.views.requests.post")
    def test_calls_openai_api_for_gpt_models(self, mock_post, mock_permission):
        """Should call OpenAI API with system message for GPT models."""
        mock_permission.return_value = None
        self.client.force_login(self.user)

        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": '{"form": {}}'}}]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        response = self.client.post(
            "/cgimail-editor/api/generate/",
            data=json.dumps(
                {
                    "mode": "create",
                    "surrogate": "askus",
                    "subject": "Test",
                    "description": "Test form",
                    "documentation": [],
                    "system_prompt": "Help",
                    "model": "gpt-4o",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

        # Verify API was called with system message and temperature
        call_args = mock_post.call_args
        payload = call_args[1]["json"]
        self.assertEqual(len(payload["messages"]), 2)
        self.assertEqual(payload["messages"][0]["role"], "system")
        self.assertEqual(payload["temperature"], 0.2)

    @override_settings(OPENAI_CGIMAIL_KEY="test-key")
    @patch("cgimail_editor.views.check_loop_permission")
    @patch("cgimail_editor.views.requests.post")
    def test_calls_openai_api_for_reasoning_models(self, mock_post, mock_permission):
        """Should call OpenAI API without system message for o1/o3 models."""
        mock_permission.return_value = None
        self.client.force_login(self.user)

        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": '{"form": {}}'}}]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        response = self.client.post(
            "/cgimail-editor/api/generate/",
            data=json.dumps(
                {
                    "mode": "create",
                    "surrogate": "askus",
                    "subject": "Test",
                    "description": "Test form",
                    "documentation": [],
                    "system_prompt": "Help",
                    "model": "o3",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

        # Verify API was called with only user message, no temperature
        call_args = mock_post.call_args
        payload = call_args[1]["json"]
        self.assertEqual(len(payload["messages"]), 1)
        self.assertEqual(payload["messages"][0]["role"], "user")
        self.assertNotIn("temperature", payload)


class HelperFunctionTests(TestCase):
    """Test helper functions."""

    def test_extract_json_from_code_block(self):
        """Should extract JSON from markdown code blocks."""
        text = '```json\n{"key": "value"}\n```'
        result = _extract_json(text)
        self.assertEqual(result, '{"key": "value"}')

    def test_extract_json_from_raw_json(self):
        """Should extract raw JSON."""
        text = 'Some text {"key": "value"} more text'
        result = _extract_json(text)
        self.assertEqual(result, '{"key": "value"}')

    def test_build_prompt_for_create_mode(self):
        """Should build correct prompt for create mode."""
        prompt = _build_prompt(
            mode="create",
            surrogate="askus",
            subject="Test Subject",
            description="Make a form",
            existing_json=None,
            documentation=[],
            schema_content="schema here",
        )
        self.assertIn("Create New Form", prompt)
        self.assertIn("askus", prompt)
        self.assertIn("Test Subject", prompt)
        self.assertIn("Make a form", prompt)

    def test_build_prompt_for_edit_mode(self):
        """Should build correct prompt for edit mode."""
        prompt = _build_prompt(
            mode="edit",
            surrogate="",
            subject="",
            description="Add phone field",
            existing_json='{"form": {}}',
            documentation=[],
            schema_content="schema here",
        )
        self.assertIn("Edit Existing Form", prompt)
        self.assertIn("Add phone field", prompt)
        self.assertIn('{"form": {}}', prompt)

    def test_extract_page_content_with_title(self):
        """Should extract title from page."""
        page = Mock()
        page.title = "Test Title"

        content = _extract_page_content(page)
        self.assertIn("<h1>Test Title</h1>", content)
