from units.models import UnitPage
from staff.utils import print_org_dict, make_org_dict
import json

hr = UnitPage.objects.get(title="Human Resources")
infotech = UnitPage.objects.get(pk=2224)
payments = UnitPage.objects.get(title="Payments")
research = UnitPage.objects.get(title="Research & Learning")
