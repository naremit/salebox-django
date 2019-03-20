from django.http import JsonResponse
from django.template.loader import render_to_string

from saleboxdjango.models import UserAddress


class SaleboxAddress:
    def __init__(self, user, address_type='d'):
        self.query = UserAddress \
                        .objects \
                        .filter(user=user) \
                        .filter(address_type=address_type)

    def get_list(self, selected_id=None):
        addresses = self.query.clone()

        # remove duplicate defaults
        # should never be needed, but here as a safety measure
        default_count = 0
        for a in addresses:
            if a.default:
                default_count += 1
                if default_count > 1:
                    a.default = False
                    a.save()

        # add "selected" attribute to all addresses
        if len(addresses) > 0:
            selected_set = False
            for a in addresses:
                a.selected = False
                if a.id == selected_id:
                    a.selected = True
                    selected_set = True

            if not selected_set:
                for a in addresses:
                    if a.default:
                        a.selected = True
                        selected_set = True
                        break

            if not selected_set:
                a[0].default = True
                a[0].save()
                a[0].selected = True

        return addresses

    def get_selected(self, selected_id):
        addresses = self.get_list()
        for a in addresses:
            if a.id == selected_id:
                return a

    def remove_address(self, id):
        address = self.query.clone().filter(id=id).delete()

    def render_partial(
            self,
            show_checkbox,
            selected_id=None,
            template='salebox/address/list_partial.html'
        ):

        return render_to_string(
            template,
            {
                'addresses': self.get_list(selected_id),
                'show_checkbox': show_checkbox
            }
        )

    def set_default(id):
        addresses = self.query.clone()

        # check selected id exists in queryset
        default_exists = False
        for a in addresses:
            if a.id == id:
                default_exists = True
                break

        # update records
        if default_exists:
            for a in addresses:
                if a.id == id:
                    if a.default != True:
                        a.default = True
                        a.save()
                else:
                    if a.default != False:
                        a.default = False
                        a.save()


