from django import forms
from .models import Item, Review, Seller

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['title', 'description', 'price', 'category']

    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        self.seller_form = SellerForm()

    def save(self, commit=True):
        item = super().save(commit=False)

        seller_form = SellerForm(self.data)
        if seller_form.is_valid():
            seller = seller_form.save()
            item.seller = seller

        if commit:
            item.save()

        return item

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['name', 'comment']

class SellerForm(forms.ModelForm):
    class Meta:
        model = Seller
        fields = ['name', 'phone_num']
        widgets = {
            'date_joined': forms.DateInput(attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        super(SellerForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['phone_num'].required = True