from units.models import UnitPage
from staff.utils import (print_org_dict,
                         make_staff_dict,
                         make_org_dict,
                         unit_to_line,
                         unit_to_lines,
                         org_dict_to_mermaid,
                         cache_unit_json,
                         cache_lookup,
                         update_org_chart_cache
                         )
                         
import json

infotech = UnitPage.objects.get(pk=2224)
rl = UnitPage.objects.get(title="Research & Learning")
