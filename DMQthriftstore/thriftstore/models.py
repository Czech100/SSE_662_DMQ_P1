from django.db import models
from django.utils import timezone


# Create your models here.

class Item(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    is_sold = models.BooleanField(default=False)
    sold_at = models.DateTimeField(null=True, blank=True)
    
    
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