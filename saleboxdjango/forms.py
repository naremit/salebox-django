from django import forms


class BasketForm(forms.Form):
    variant_id = forms.IntegerField()
    quantity = forms.IntegerField()
    relative = forms.BooleanField()


class WishlistForm(forms.Form):
    variant_id = forms.IntegerField()
    add = forms.BooleanField()
