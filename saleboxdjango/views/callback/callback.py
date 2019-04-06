from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from saleboxdjango.models import CallbackStore

class SaleboxCallbackView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        CallbackStore(
            ip_address=request.META['REMOTE_ADDR'],
            method=request.method.lower(),
            post=request.POST
        ).save()

        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return HttpResponse('OK')

    def post(self, request):
        return HttpResponse('OK')
