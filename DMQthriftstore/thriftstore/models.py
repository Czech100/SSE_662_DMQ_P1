from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator


# Create your models here.

PRICE_MAX_DIGITS = 10
PRICE_DECIMAL_PLACES = 2


class Seller(models.Model):
    name = models.CharField(max_length = 40)
    date_joined = models.DateTimeField(auto_now_add=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_num = models.CharField(validators=[phone_regex], max_length=17, blank=True)  

    def __str__(self):
        return f"Sold by {self.name} contact at {self.phone_num}"


class Item(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=PRICE_MAX_DIGITS, decimal_places=PRICE_DECIMAL_PLACES)
    is_sold = models.BooleanField(default=False, null=False, blank=False)
    sold_at = models.DateTimeField(null=True, blank=True)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)


    CATEGORY_CHOICES = (
        ('CLOTHING', 'Clothing'),
        ('ELECTRONICS', 'Electronics'),
        ('BOOKS', 'Books'),
        ('FURNITURE', 'Furniture'),
    )
    
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='CLOTHING')
    
    def mark_as_sold(self):
        self.is_sold = True
        self.sold_at = timezone.now()
        self.save()

    def save(self, *args, **kwargs):
        assert self.price > 0, "Price must be positive"
        super().save(*args, **kwargs)



class Review(models.Model):
    name = models.CharField(max_length=100)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.name} on {self.created_at.strftime('%Y-%m-%d %H:%M')}"