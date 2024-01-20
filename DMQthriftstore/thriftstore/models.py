from django.db import models
from django.utils import timezone


# Create your models here.


class Seller(models.Model):
    name = models.CharField(max_length = 40)
    date_joined = models.DateTimeField()
    phone_num = models.IntegerField()

    def __str__(self):
        return f"Sold by {self.name} contact at {self.phone_num}"


class Item(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    is_sold = models.BooleanField(default=False)
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


class Review(models.Model):
    name = models.CharField(max_length=100)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.name} on {self.created_at.strftime('%Y-%m-%d %H:%M')}"