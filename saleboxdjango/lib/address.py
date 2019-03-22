from django.http import JsonResponse
from django.template.loader import render_to_string

from saleboxdjango.models import UserAddress


class SaleboxAddress:
    def __init__(self, user, address_group='default'):
        self.query = UserAddress \
                        .objects \
                        .filter(user=user) \
                        .filter(address_group=address_group) \
                        .select_related('country', 'country_state')

    def get_count(self):
        return self.query.all().count()

    def get_list(self, selected_id=None):
        addresses = self.query.all()

        # add "selected" attribute to all addresses
        if len(addresses) > 0:
            has_selected = False
            for a in addresses:
                a.selected = False
                if a.id == selected_id:
                    a.selected = True
                    has_selected = True

            if not has_selected:
                for a in addresses:
                    if a.default:
                        a.selected = True
                        break

        # make a list of the non-null address lines
        for a in addresses:
            a.address_list = []
            for i in range(1, 6):
                tmp = getattr(a, 'address_%s' % i, None)
                if tmp:
                    a.address_list.append(tmp)

        return addresses

    def get_single_by_default(self):
        return self.query.all().get(default=True)

    def get_single_by_id(self, id):
        return self.query.all().get(id=id)

    def remove_address(self, id):
        address = self.query.all().get(id=id)
        address.delete()

    def render_partial(
            self,
            show_checkbox,
            selected_id=None,
            template='salebox/address/list.html'
        ):

        return render_to_string(
            template,
            {
                'addresses': self.get_list(selected_id),
                'show_checkbox': show_checkbox
            }
        )

    def set_default(self, id):
        address = self.get_single_by_id(id)
        if not address.default:
            address.default = True
            address.save()

