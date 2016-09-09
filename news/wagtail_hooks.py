from django.conf.urls import url
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render
from wagtail.wagtailadmin.menu import MenuItem
from wagtail.wagtailcore import hooks

from .forms import EmailNotificationTestForm
from .utils import send_loop_news_email_notifications

def admin_view(request):
    if request.method == 'POST':
        form = EmailNotificationTestForm(request.POST)
        if form.is_valid():
            from_email = form.data.get('from_email', None)
            to_email = form.data.get('to_email', None)
            num_days = form.data.get('num_days', None)
            end_date = form.data.get('end_date', None)
           
            if from_email != None and to_email != None and num_days != None and end_date != None: 
                send_loop_news_email_notifications(from_email, to_email, num_days, end_date)
            return render(request, 'news/loop_news_notifications_thanks.html', {})
        else:
            return render(request, 'news/loop_news_notifications.html', {'form': form})
    else:
        form = EmailNotificationTestForm()
        return render(request, 'news/loop_news_notifications.html', {'form': form})

@hooks.register('register_admin_urls')
def urlconf_time():
    return [
        url(r'^loopnotifications/$', admin_view, name='loopnotifications')
    ]

@hooks.register('register_settings_menu_item')
def register_frank_menu_item():
  return MenuItem('Loop News Notifications', reverse('loopnotifications'), classnames='icon icon-mail', order=10000)
