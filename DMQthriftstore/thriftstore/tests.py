from django.test import TestCase
from .models import Item

# Create your tests here.

class ItemModelTest(TestCase):
    def test_item_creation(self):
        item = Item.objects.create(title="Test Item", description = "Just a test item.", price=9.99)
        self.assertEqual(item.title, "Test Item")
