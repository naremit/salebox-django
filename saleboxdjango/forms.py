from django import forms


class BasketForm(forms.Form):
    variant_id = forms.IntegerField()
    quantity = forms.IntegerField()
    relative = forms.BooleanField()


class RatingForm(forms.Form):
    variant_id = forms.IntegerField()
    rating = forms.IntegerField(min_value=0, max_value=100)


class WishlistForm(forms.Form):
    variant_id = forms.IntegerField()
    add = forms.BooleanField()
