from units.models import UnitPage
from staff.utils import (print_org_dict,
                         make_staff_dict,
                         make_org_dict,
                         unit_to_line,
                         unit_to_lines,
                         staff_diagram,
                         org_dict_to_mermaid,
                         )
                         
import json

infotech = UnitPage.objects.get(pk=2224)
rl = UnitPage.objects.get(title="Research & Learning")
