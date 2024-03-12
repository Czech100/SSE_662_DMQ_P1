from django import forms
from .models import Item, Review, Seller

# Form to create or update an Item instance
class ItemForm(forms.ModelForm):
    class Meta:
        model = Item  # The model associated with this form
        fields = ['title', 'description', 'price', 'category']  # Fields included in the form

    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        self.seller_form = SellerForm()  # Initialize a SellerForm for seller information

    def save(self, commit=True):
        item = super().save(commit=False)  # Save the form's data into an Item instance without committing to the database

        seller_form = SellerForm(self.data)
        if seller_form.is_valid():
            seller = seller_form.save()  # Save the seller form data
            item.seller = seller  # Link the item to its seller

        if commit:
            item.save()  # Commit the item to the database

        return item  # Return the saved Item instance

# Form to create or update a Review instance
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review  # The model associated with this form
        fields = ['name', 'comment']  # Fields included in the form

# Form to create or update a Seller instance
class SellerForm(forms.ModelForm):
    class Meta:
        model = Seller  # The model associated with this form
        fields = ['name', 'phone_num']  # Fields included in the form
        widgets = {
            'date_joined': forms.DateInput(attrs={'type': 'date'})  # Use a date input for the 'date_joined' field
        }

    def __init__(self, *args, **kwargs):
        super(SellerForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = True  # The 'name' field is required
        self.fields['phone_num'].required = True  # The 'phone_num' field is required
