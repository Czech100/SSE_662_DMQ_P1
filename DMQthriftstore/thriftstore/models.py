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
