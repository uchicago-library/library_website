from library_website.settings.base import DEFAULT_UNIT

def get_default_unit():
    """
    Get a fallback unit by ID from the config
    if no unit is set.

    Returns:
        UnitPage object
    """
    from units.models import UnitPage
    return UnitPage.objects.live().filter(id=DEFAULT_UNIT)[0]
