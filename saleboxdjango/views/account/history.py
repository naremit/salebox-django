from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView


class SaleboxAccountHistoryView(TemplateView):
    template_name = 'salebox/account/history.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['user'] = request.user
        context['member'] = request.user.get_member()

        from apps.user.models import User
        u = User.objects.get(id=19)
        context['user'] = u
        context['member'] = u.get_member()

        context['member'].transactionhistory_get_data()
        return self.render_to_response(context)