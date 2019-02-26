from django import forms


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
