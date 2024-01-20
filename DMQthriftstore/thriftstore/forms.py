from django import forms
from .models import Item, Review, Seller


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['title', 'description', 'price', 'seller']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['name', 'comment']

class SellerForm(forms.ModelForm):
    class Meta:
        model = Seller
        fields = ['name', 'date_joined', 'phone_num']