from datetime import timedelta

from django import forms
from django.http import JsonResponse
from django.utils.timezone import now
from django.views.generic import View

from saleboxdjango.models import Analytic
from user_agents import parse


class SaleboxAnalyticsForm(forms.Form):
    key = forms.UUIDField()

class SaleboxAnalyticsView(View):
    def post(self, request):
        form = SaleboxAnalyticsForm(request.POST)
        if form.is_valid():
            row = Analytic \
                    .objects \
                    .filter(key=form.cleaned_data['key']) \
                    .filter(first_seen__gt=now() - timedelta(hours=24)) \
                    .first()

            if row is None:
                # get ua
                ua_string = request.META.get('HTTP_USER_AGENT', None)
                if ua_string is not None:
                    ua = parse(ua_string)

                    # add to db
                    row = Analytic(
                        key=form.cleaned_data['key'],
                        ip_address=request.META.get('REMOTE_ADDR', None),
                        ua_browser_family=ua.browser.family[:20] if ua.browser.family else None,
                        ua_browser_version=ua.browser.version_string[:20] if ua.browser.version_string else None,
                        ua_os_family=ua.os.family[:20] if ua.os.family else None,
                        ua_os_version=ua.os.version_string[:20] if ua.os.version else None,
                        ua_device_family=ua.device.family[:20] if ua.device.family else None,
                        ua_device_brand=ua.device.brand[:20] if ua.device.brand else None,
                        ua_device_model=ua.device.model[:20] if ua.device.model else None,
                        ua_is_mobile=ua.is_mobile,
                        ua_is_tablet=ua.is_tablet,
                        ua_is_touch_capable=ua.is_touch_capable,
                        ua_is_pc=ua.is_pc,
                        ua_is_bot=ua.is_bot
                    )
                    row.save()
            else:
                # update page_views
                row.page_views = row.page_views + 1
                row.save()

        return JsonResponse({'thank':'you'})