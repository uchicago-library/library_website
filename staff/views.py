import requests

from base.wagtail_hooks import (
    get_required_groups, has_permission, redirect_users_without_permissions
)
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import render
from intranetunits.models import IntranetUnitsPage
from public.models import LocationPage
from rest_framework.authentication import (
    SessionAuthentication, TokenAuthentication
)
from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes
)
from rest_framework.permissions import IsAuthenticated
from staff.models import StaffPage, StaffPageSubjectPlacement
from subjects.models import Subject
from units.views import get_staff_pages_for_unit
from wagtail.models import Site
from wagtail.images.models import Image


def staff(request):
    department = request.GET.get('department', None)
    library = request.GET.get('library', None)
    query = request.GET.get('query', None)
    subject = request.GET.get('subject', None)
    view = request.GET.get('view', 'staff')

    loop_homepage = Site.objects.get(site_name='Loop').root_page
    if not has_permission(request.user, get_required_groups(loop_homepage)):
        return redirect_users_without_permissions(
            loop_homepage, request, None, None
        )

    staff_pages = []
    flat_units = []

    if view == 'staff':
        if department:
            staff_pages = get_staff_pages_for_unit(department, True, True)
        elif library:
            staff_pages = StaffPage.get_staff_by_building(library)
        else:
            staff_pages = StaffPage.objects.live().order_by(
                'last_name', 'first_name'
            )

        if subject:
            subject_pk = Subject.objects.get(name=subject).pk
            staff_pks = StaffPageSubjectPlacement.objects.filter(
                subject=subject_pk
            ).values_list('page', flat=True).distinct()

            if staff_pages:
                staff_pages = staff_pages.filter(
                    pk__in=staff_pks
                ).order_by('last_name', 'first_name')
            else:
                staff_pages = StaffPage.objects.filter(
                    pk__in=staff_pks
                ).order_by('last_name', 'first_name')

        if query:
            if staff_pages:
                staff_pages = staff_pages.search(query)
            else:
                staff_pages = StaffPage.objects.live().search(query)

        if not department and not library and not subject and not query:
            staff_pages = StaffPage.objects.live().order_by('title').order_by(
                'last_name', 'first_name'
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
    subject_pks = StaffPageSubjectPlacement.objects.all().values_list(
        'subject', flat=True
    ).distinct()
    subjects = Subject.objects.filter(pk__in=subject_pks
                                      ).values_list('name', flat=True)

    default_image = Image.objects.get(title="Default Placeholder Photo")

    return render(
        request, 'staff/staff_index_page.html', {
            'default_image':
            default_image,
            'department':
            department,
            'flat_intranet_units':
            flat_units,
            'libraries': [
                str(p)
                for p in LocationPage.objects.live().filter(is_building=True)
            ],
            'library':
            library,
            'query':
            query,
            'subject':
            subject,
            'subjects':
            subjects,
            'subjects':
            subjects,
            'staff_pages':
            staff_pages,
            'view':
            view
        }
    )


@api_view(['GET'])
@authentication_classes((SessionAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
def staff_api(request):
    """
    API view for getting information about staff members. The request must
    provide a user token in the headers. In order to make tokenization work,
    the Django Rest Framework requires us to use the @api_view decorator.
    Since we can't directly apply this to the Wagtail API (built on Django
    Rest Framework) we apply it here and pass the request on to the default
    Wagtail API. We return the response that Wagtail API gives us. To edit
    or add fields to this API go to the StaffPage model.

    This view only passes the request to the Wagtail pages API and returns
    the output. The view will only be rendered if the request headers contain
    a token. Any user can have a token, however, we do not create them by
    default.

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
        copy = request.GET.copy()
        params = copy.urlencode()
        scheme = request.is_secure() and 'https' or 'http'
        base_url = scheme + '://' + request.get_host()
        rest_url = base_url + '/api/v2/pages/?' + params

        try:
            token = request.META['HTTP_AUTHORIZATION']
            rest_headers = {'Authorization': token}
            rest_response = requests.get(rest_url, headers=rest_headers)
            return JsonResponse(rest_response.json())
        except (KeyError):
            raise PermissionDenied
    raise PermissionDenied
