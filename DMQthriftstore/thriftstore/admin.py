from django.contrib import admin

# Register your models here.
from .models import Seller, Item, Review

admin.site.register(Seller)
admin.site.register(Item)
admin.site.register(Review)
