from datetime import timedelta

from django import forms
from django.contrib.gis.geoip2 import GeoIP2
from django.http import JsonResponse
from django.utils.timezone import now
from django.views.generic import View

from user_agents import parse

from saleboxdjango.models import Analytic


class SaleboxAnalyticsForm(forms.Form):
    key = forms.UUIDField()
    lang = forms.CharField(required=False)
    width = forms.IntegerField(required=False)
    height = forms.IntegerField(required=False)

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

                    ip_address = request.META.get('REMOTE_ADDR', None)
                    ip_country = None
                    ip_city = None
                    ip_tz = None
                    ip_lat = None
                    ip_lng = None
                    if ip_address is not None:
                        try:
                            g = GeoIP2()
                            tmp = g.city(ip_address)
                            ip_country = tmp['country_code']
                            ip_city = tmp['city']
                            ip_tz = tmp['time_zone']
                            ip_lat = tmp['latitude']
                            ip_lng = tmp['longitude']
                        except:
                            pass

                    # add to db
                    row = Analytic(
                        key=form.cleaned_data['key'],
                        ip_address=ip_address,
                        ip_country=ip_country,
                        ip_city=ip_city,
                        ip_tz=ip_tz,
                        ip_lat=ip_lat,
                        ip_lng=ip_lng,
                        ua_browser_family=ua.browser.family[:32] if ua.browser.family else None,
                        ua_browser_version=ua.browser.version_string[:20] if ua.browser.version_string else None,
                        ua_os_family=ua.os.family[:20] if ua.os.family else None,
                        ua_os_version=ua.os.version_string[:20] if ua.os.version else None,
                        ua_device_family=ua.device.family[:32] if ua.device.family else None,
                        ua_device_brand=ua.device.brand[:20] if ua.device.brand else None,
                        ua_device_model=ua.device.model[:20] if ua.device.model else None,
                        ua_is_mobile=ua.is_mobile,
                        ua_is_tablet=ua.is_tablet,
                        ua_is_touch_capable=ua.is_touch_capable,
                        ua_is_pc=ua.is_pc,
                        ua_is_bot=ua.is_bot,
                        language=form.cleaned_data['lang'][:10],
                        screen_width=form.cleaned_data['width'],
                        screen_height=form.cleaned_data['height']
                    )
                    row.save()
            else:
                # update page_views
                row.page_views = row.page_views + 1
                row.save()

        return JsonResponse({'thank':'you'})