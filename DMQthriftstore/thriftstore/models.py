from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator

# Constants for price field constraints
PRICE_MAX_DIGITS = 10
PRICE_DECIMAL_PLACES = 2

# Model for sellers
class Seller(models.Model):
    name = models.CharField(max_length=40)
    date_joined = models.DateTimeField(auto_now_add=True)  # Automatically set to now when object is created
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number format: '+999999999'. Up to 15 digits.")
    phone_num = models.CharField(validators=[phone_regex], max_length=17, blank=True)  # Optional phone number field

    def __str__(self):
        # String representation of a Seller
        return f"Sold by {self.name} contact at {self.phone_num}"

# Model for items
class Item(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=PRICE_MAX_DIGITS, decimal_places=PRICE_DECIMAL_PLACES)
    is_sold = models.BooleanField(default=False)
    sold_at = models.DateTimeField(null=True, blank=True)  # Timestamp for when the item was sold
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)  # Link to the Seller model

    # Choices for the category of the item
    CATEGORY_CHOICES = (
        ('CLOTHING', 'Clothing'),
        ('ELECTRONICS', 'Electronics'),
        ('BOOKS', 'Books'),
        ('FURNITURE', 'Furniture'),
    )
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='CLOTHING')
    
    def mark_as_sold(self):
        # Mark the item as sold and set the sold_at timestamp
        self.is_sold = True
        self.sold_at = models.DateTimeField(auto_now_add=True)
        self.save()

    def save(self, *args, **kwargs):
        # Custom save method to ensure price is positive
        assert self.price > 0, "Price must be positive"
        super().save(*args, **kwargs)

# Model for reviews
class Review(models.Model):
    name = models.CharField(max_length=100)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the review was created

    def __str__(self):
        # String representation of a Review
        return f"Review by {self.name} on {self.created_at.strftime('%Y-%m-%d %H:%M')}"
