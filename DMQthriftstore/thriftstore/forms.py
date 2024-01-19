from django import forms
from .models import Item, Review


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['title', 'description', 'price']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['name', 'comment']