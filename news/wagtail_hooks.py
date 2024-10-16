from django.shortcuts import render
from django.urls import re_path, reverse
from wagtail import hooks
from wagtail.admin.menu import MenuItem

from .forms import EmailNotificationTestForm
from .utils import send_loop_news_email_notifications


def admin_view(request):
    if request.method == 'POST':
        form = EmailNotificationTestForm(request.POST)
        if form.is_valid():
            from_email = form.data.get('email_from', None)
            to_email = form.data.get('email_to', None)
            num_days = form.data.get('num_days', None)
            if num_days:
                num_days = int(num_days)
            # strip dashes out of the date, so YYYY-MM-DD becomes YYYYMMDD
            end_date = form.data.get('email_as_if_date', None)
            if end_date:
                end_date = end_date.replace("-", "")

            if (
                from_email is not None
                and to_email is not None
                and num_days is not None
                and end_date is not None
            ):
                send_loop_news_email_notifications(
                    from_email, to_email, num_days, end_date
                )
            return render(request, 'news/loop_news_notifications_thanks.html', {})
        else:
            return render(request, 'news/loop_news_notifications.html', {'form': form})
    else:
        form = EmailNotificationTestForm()
        return render(request, 'news/loop_news_notifications.html', {'form': form})


@hooks.register('register_admin_urls')
def urlconf_time():
    return [re_path(r'^loopnotifications/$', admin_view, name='loopnotifications')]


@hooks.register('register_settings_menu_item')
def register_frank_menu_item():
    return MenuItem(
        'Loop News Notifications',
        reverse('loopnotifications'),
        classname='icon icon-mail',
        order=10000,
    )
