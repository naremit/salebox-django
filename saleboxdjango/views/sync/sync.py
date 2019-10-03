from django import forms
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from saleboxdjango.models import LastUpdate


class SaleboxSyncForm(forms.Form):
    key = forms.CharField()
    license = forms.CharField()


@csrf_exempt
def SaleboxSyncView(request):
    success = False

    # is this a POST?
    if request.method == 'POST':
        # did it come from the server IP?
        if settings.SALEBOX['API']['IP'] == request.META['REMOTE_ADDR']:
            # did it send a valid key / license combo?
            form = SaleboxSyncForm(request.POST)
            if form.is_valid():
                if  settings.SALEBOX['API']['KEY'] == str(form.cleaned_data['key']) and \
                    settings.SALEBOX['API']['LICENSE'] == str(form.cleaned_data['license']):
                    # ok, we're good. reset the LastUpdate value
                    lu = LastUpdate \
                            .objects \
                            .filter(code='saleboxsync_pull_start') \
                            .filter(value__gt=0) \
                            .first()
                    if lu is not None:
                        lu.value = 0
                        lu.save()
                    return JsonResponse({ 'status': 'OK' })

    # fallback
    return JsonResponse({ 'status': 'Fail' })