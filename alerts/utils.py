import bleach


def get_alert(current_site):
    """
    Get an alert banner for display if an AlertPage is published.

    Args:
        current_site: Wagtail site object.

    Returns:
        None, if no AlertPage is found, otherwise if an AlertPage
        is published, returns a tuple of  strings representing an
        alert where the first item is a banner message, the second
        item is the level of the alert (to be used as a css class),
        the third item is rich text, and the fourth item is a url.
    """
    from .models import AlertPage
    info_alert = AlertPage.objects.live().filter(alert_level='alert-info')
    high_alert = AlertPage.objects.live().filter(alert_level='alert-high')

    if not high_alert and not info_alert:
        return None
    else:
        alert = high_alert[0] if high_alert else info_alert[0]
        msg = bleach.clean(
            alert.banner_message, tags=['p', 'b', 'a', 'strong'], strip=True
        )
        return (
            msg, alert.alert_level, alert.more_info,
            alert.relative_url(current_site)
        )


def get_browse_alerts(current_site):
    """
    Get all the banner alert related varibles needed to populate context
    for regular Django views.

    Args:
        current_site: Wagtail site object.

    Returns:
        A tuple where the first value is a boolean and the second value
        is a tuple of (False, False, False, False) or banner related
        context variables.
    """
    has_alert = False if not get_alert(current_site) else True
    alert_context_vars = (False, False, False, False)
    if has_alert:
        alert_context_vars = get_alert(current_site)
    return (has_alert, alert_context_vars)
