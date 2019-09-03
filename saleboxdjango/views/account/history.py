from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView


class SaleboxAccountHistoryListView(TemplateView):
    template_name = 'salebox/account/history_list.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['user'] = request.user
        context['member'] = request.user.get_member()
        context['member'].transactionhistory_get_data()

        # filter data depenent on search
        s = request.GET.get('filter', '').lower()
        if len(s) > 0:
            context['member'].salebox_transactionhistory_data = [
                d for d in context['member'].salebox_transactionhistory_data if s in d['pos_guid'].lower()
            ]

        return self.render_to_response(context)


class SaleboxAccountHistoryDetailView(TemplateView):
    template_name = 'salebox/account/history_detail.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['user'] = request.user

        try:
            member = context['user'].get_member()
            context['member'] = member
            context['member'].transactionhistory_get_data()
            context['transaction'] = member.transactionhistory_get_single_transaction(self.kwargs['id'])
        except:
            raise Http404

        # check transaction exists
        if context['transaction'] is None:
            raise Http404

        return self.render_to_response(context)