from base.wagtail_hooks import (
    get_required_groups,
    has_permission,
    redirect_users_without_permissions,
)
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import render
from intranetunits.models import IntranetUnitsPage
from library_website.api import api_router
from public.models import LocationPage
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from subjects.models import Subject
from units.views import get_staff_pages_for_unit
from wagtail.api.v2.views import PagesAPIViewSet
from wagtail.images.models import Image
from wagtail.models import Site
from wagtailcache.cache import nocache_page

from staff.models import StaffPage, StaffPageSubjectPlacement


def staff(request):
    department = request.GET.get('department', None)
    library = request.GET.get('library', None)
    query = request.GET.get('query', None)
    subject = request.GET.get('subject', None)
    view = request.GET.get('view', 'staff')

    loop_homepage = Site.objects.get(site_name='Loop').root_page
    if not has_permission(request.user, get_required_groups(loop_homepage)):
        return redirect_users_without_permissions(loop_homepage, request, None, None)

    staff_pages = []
    flat_units = []

    if view == 'staff':
        if department:
            staff_pages = get_staff_pages_for_unit(department, True, True)
        elif library:
            staff_pages = StaffPage.get_staff_by_building(library)
        else:
            staff_pages = StaffPage.objects.live().order_by('last_name', 'first_name')

        if subject:
            subject_pk = Subject.objects.get(name=subject).pk
            staff_pks = (
                StaffPageSubjectPlacement.objects.filter(subject=subject_pk)
                .values_list('page', flat=True)
                .distinct()
            )

            if staff_pages:
                staff_pages = staff_pages.filter(pk__in=staff_pks).order_by(
                    'last_name', 'first_name'
                )
            else:
                staff_pages = StaffPage.objects.filter(pk__in=staff_pks).order_by(
                    'last_name', 'first_name'
                )

        if query:
            if staff_pages:
                staff_pages = staff_pages.search(query)
            else:
                staff_pages = StaffPage.objects.live().search(query)

        if not department and not library and not subject and not query:
            staff_pages = (
                StaffPage.objects.live()
                .order_by('title')
                .order_by('last_name', 'first_name')
            )
    elif view == 'department':
        if query:
            intranetunits_qs = IntranetUnitsPage.objects.live().search(query)
        else:
            intranetunits_qs = IntranetUnitsPage.objects.live()
        for i in intranetunits_qs:
            try:
                i_library = i.unit_page.get_building()
                i_title = i.get_full_name()
            except AttributeError:
                continue
            flat_units.append(
                {
                    'internal_location': i.internal_location,
                    'internal_phone_number': i.internal_phone_number,
                    'library': i_library,
                    'title': i_title,
                    'url': i.url,
                }
            )
        flat_units = sorted(flat_units, key=lambda k: k['title'])

    # Subjects
    subject_pks = (
        StaffPageSubjectPlacement.objects.all()
        .values_list('subject', flat=True)
        .distinct()
    )
    subjects = Subject.objects.filter(pk__in=subject_pks).values_list('name', flat=True)

    default_image = Image.objects.get(title="Default Placeholder Photo")

    return render(
        request,
        'staff/staff_index_page.html',
        {
            'default_image': default_image,
            'department': department,
            'flat_intranet_units': flat_units,
            'libraries': [
                str(p) for p in LocationPage.objects.live().filter(is_building=True)
            ],
            'library': library,
            'query': query,
            'subject': subject,
            'subjects': subjects,
            'subjects': subjects,
            'staff_pages': staff_pages,
            'view': view,
        },
    )


@nocache_page
@api_view(['GET'])
@authentication_classes((SessionAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
def staff_api(request):
    """
    API view for getting information about staff members. The request must
    provide a user token in the headers. In order to make tokenization work,
    the Django Rest Framework requires us to use the @api_view decorator.
    Since we can't directly apply this to the Wagtail API (built on Django
    Rest Framework) we apply it here and call the Wagtail API view directly.
    To edit or add fields to this API go to the StaffPage model.

    This view calls the Wagtail pages API view directly without making an
    HTTP request. The view will only be rendered if the request headers contain
    a token or if the user is session authenticated. Any user can have a token,
    however, we do not create them by default.

    Create and view a token for a given user:
    from rest_framework.authtoken.models import Token
    from django.contrib.auth.models import User
    u = User.objects.get(username='tdanstrom')
    token = Token.objects.create(user=u)
    print(token)

    More info:
    django-rest-framework.org/api-guide/authentication/#tokenauthentication

    Example query:
    curl -X GET 'https://loop.lib.uchicago.edu/staff_api/?format=json&limit=1000&type=staff.StaffPage&fields=*' -H 'Authorization: Token 364893-PRIVATE-TOKEN'
    """

    if request.method == 'GET':
        # Get the Wagtail Pages API viewset and create a view instance for listing
        # Note: Wagtail uses 'listing_view' instead of the standard DRF 'list' action
        view_instance = PagesAPIViewSet.as_view({'get': 'listing_view'})

        # Get the underlying Django request and add the router reference
        # The @api_view decorator wraps the HttpRequest in a DRF Request,
        # so we need to use request._request to get the original Django request.
        # The Wagtail API requires a 'wagtailapi_router' attribute on the request.
        django_request = request._request
        django_request.wagtailapi_router = api_router

        # Call the view with the prepared request
        # Authentication has already been handled by @authentication_classes,
        # so django_request.user is properly set to the authenticated user.
        response = view_instance(django_request)

        # Return the response data as JSON
        return JsonResponse(response.data)

    raise PermissionDenied
