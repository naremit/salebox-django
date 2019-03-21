from django import forms


class SaleboxForm(forms.Form):
    redirect = forms.CharField(required=False)
    results = forms.CharField(required=False)
    state = forms.CharField(required=False)

class SaleboxAddressAddForm(SaleboxForm):
    address_group = forms.CharField(required=False)
    set_default = forms.BooleanField(required=False)
    full_name = forms.CharField(max_length=150)
    address_1 = forms.CharField(max_length=150)
    address_2 = forms.CharField(max_length=150)
    address_3 = forms.CharField(max_length=150, required=False)
    address_4 = forms.CharField(max_length=150, required=False)
    address_5 = forms.CharField(max_length=150, required=False)
    country_state = forms.IntegerField(required=False)
    country = forms.IntegerField(required=False)
    postcode = forms.CharField(max_length=12, required=False)


class SaleboxAddressIDForm(SaleboxForm):
    id = forms.IntegerField()




class BasketForm(forms.Form):
    variant_id = forms.IntegerField()
    quantity = forms.IntegerField()
    relative = forms.BooleanField(required=False)
    results = forms.CharField(required=False)


class RatingForm(forms.Form):
    variant_id = forms.IntegerField()
    rating = forms.IntegerField(min_value=-1, max_value=100)


class SwitchBasketWishlistForm(forms.Form):
    variant_id = forms.IntegerField()
    destination = forms.CharField()


class WishlistForm(forms.Form):
    variant_id = forms.IntegerField()
    add = forms.BooleanField(required=False)
    results = forms.CharField(required=False)
