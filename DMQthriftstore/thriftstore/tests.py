from django.test import TestCase
from .models import Item
from .forms import ItemForm
from django.utils import timezone
from django.urls import reverse

# Create your tests here.

class ItemModelTest(TestCase):
    def test_item_creation(self):
        item = Item.objects.create(title="Test Item", description = "Just a test item.", price=9.99)
        self.assertEqual(item.title, "Test Item")
        self.assertEqual(item.description, "Just a test item.")
        self.assertEqual(item.price, 9.99)


class ItemFormTest(TestCase):
    def test_form_validity(self):
        form_data = {'title': 'Test Item', 'description': 'A test item', 'price': 9.99}
        form = ItemForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_saves_item(self):
        form_data = {'title': 'Test Item', 'description': 'A test item', 'price': 9.99}
        form = ItemForm(data=form_data)
        if form.is_valid():
            new_item = form.save()
            self.assertEqual(Item.objects.count(), 1)
            self.assertEqual(new_item.title, 'Test Item')


class AddItemViewTest(TestCase):
    def test_view_renders_item_form(self):
        response = self.client.get(reverse('add_item'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        self.assertIsInstance(response.context['form'], ItemForm)

    def test_view_saves_item_with_post_request(self):
        data = {'title': 'Test Item', 'description': 'A test item', 'price': 9.99}
        self.client.post(reverse('add_item'), data)
        self.assertEqual(Item.objects.count(), 1)


class AddItemTemplateTest(TestCase):
    def test_template_displays_form_fields(self):
        response = self.client.get(reverse('add_item'))
        self.assertContains(response, 'name="title"')
        self.assertContains(response, 'name="description"')
        self.assertContains(response, 'name="price"')

class ItemBuyTest(TestCase):
    def setUp(self):
        self.item = Item.objects.create(title="Test Item", description="A test item", price=9.99, is_sold=False)

    def test_buy_item(self):
        self.client.post(reverse('buy_item', args=(self.item.id,)))
        updated_item = Item.objects.get(id=self.item.id)
        
        self.assertTrue(updated_item.is_sold)

class RecentlySoldItemsTest(TestCase):
    def test_recently_sold_items_display(self):
        sold_item = Item.objects.create(title="Sold Item", description="A sold item", price=9.99, is_sold=True, sold_at=timezone.now())
        response = self.client.get(reverse('item_list'))
        self.assertContains(response, sold_item.title)