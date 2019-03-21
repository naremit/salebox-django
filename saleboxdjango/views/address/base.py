from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.generic import View

from saleboxdjango.lib.address import SaleboxAddress


class SaleboxAddressView(LoginRequiredMixin, View):
    form = None  # django form
    action = None  # name of action performed
    status = None  # action outcome

    redirect = None  # url to redirect to (if applicable)
    state = None  # optional extra string data, passed thru
    results_csv = ''  # csv of requested results (if applicable)
    results = {}  # dict of results to return


    def get(self, request):
        return JsonResponse({})

    def post(self, request):
        self.form = self.form(request.POST)
        if self.form.is_valid():
            # init class
            self.sa = SaleboxAddress(request.user)

            # retrieve form values
            self.redirect = self.form.cleaned_data['redirect']
            self.state = self.form.cleaned_data['state']
            if self.form.cleaned_data['results']:
                self.results_csv = self.form.cleaned_data['results']

            # perform task
            self.form_valid(request)
        else:
            # handle error
            self.form_invalid(request)

        # redirect if applicable
        if self.redirect:
            self.add_querystring('state', self.state)
            self.add_querystring('action', self.action)
            self.add_querystring('status', self.status)
            return redirect(self.redirect)

        # return json
        if self.state:
            self.results['state'] = self.state
        if self.status:
            self.results['action'] = self.action
        if self.status:
            self.results['status'] = self.status
        return JsonResponse(self.results)

    def form_valid(self, request):
        pass

    def form_invalid(self, request):
        pass

    def add_querystring(self, key, value):
        if value:
            self.redirect = '%s%s%s=%s' % (
                self.redirect,
                '&' if '?' in self.redirect else '?',
                key,
                value
            )
