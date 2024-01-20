from django.test import TestCase, Client
from .models import Item, Review, Seller
from .forms import ItemForm, ReviewForm, SellerForm
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User

# Create your tests here.

class ItemModelTest(TestCase):
    def setUp(self):
        self.seller1 = Seller.objects.create(name = "Test Name", date_joined=timezone.now(), phone_num = 1234567890)

    def test_item_creation(self):
        item = Item.objects.create(title="Test Item", description = "Just a test item.", price=9.99, seller = self.seller1)
        self.assertEqual(item.title, "Test Item")
        self.assertEqual(item.description, "Just a test item.")
        self.assertEqual(item.price, 9.99)
        self.assertEqual(item.seller.id, self.seller1.id)


class ItemFormTest(TestCase):
    def setUp(self):
        self.seller1 = Seller.objects.create(name = "Test Name", date_joined=timezone.now(), phone_num = 1234567890)

    def test_form_validity(self):
        form_data = {'title': 'Test Item', 'description': 'A test item', 'price': 9.99, 'seller': self.seller1}
        form = ItemForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_saves_item(self):
        form_data = {'title': 'Test Item', 'description': 'A test item', 'price': 9.99, 'seller': self.seller1}
        form = ItemForm(data=form_data)
        if form.is_valid():
            new_item = form.save()
            self.assertEqual(Item.objects.count(), 1)
            self.assertEqual(new_item.title, 'Test Item')


class AddItemViewTest(TestCase):
    def setUp(self):
        self.seller1 = Seller.objects.create(name = "Test Name", date_joined=timezone.now(), phone_num = 1234567890)

    def test_view_renders_item_form(self):
        response = self.client.get(reverse('add_item'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        self.assertIsInstance(response.context['form'], ItemForm)

    def test_view_saves_item_with_post_request(self):
        data = {'title': 'Test Item', 'description': 'A test item', 'price': 9.99, 'seller': self.seller1}
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
        self.seller1 = Seller.objects.create(name = "Test Name", date_joined=timezone.now(), phone_num = 1234567890)
        self.item = Item.objects.create(title="Test Item", description="A test item", price=9.99, is_sold=False, seller = self.seller1)

    def test_buy_item(self):
        self.client.post(reverse('buy_item', args=(self.item.id,)))
        updated_item = Item.objects.get(id=self.item.id)
        
        self.assertTrue(updated_item.is_sold)

class RecentlySoldItemsTest(TestCase):
    def setUp(self):
        self.seller1 = Seller.objects.create(name = "Test Name", date_joined=timezone.now(), phone_num = 1234567890)
       
    def test_recently_sold_items_display(self):
        sold_item = Item.objects.create(title="Sold Item", description="A sold item", price=9.99, is_sold=True, sold_at=timezone.now(), seller = self.seller1)
        response = self.client.get(reverse('item_list'))
        self.assertContains(response, sold_item.title)

class CartTests(TestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(username='testuser', password='testpass')
        # Create some sellers
        self.seller1 = Seller.objects.create(name = "Test Name", date_joined=timezone.now(), phone_num = 1234567890)
        self.seller2 = Seller.objects.create(name = "Test Name1", date_joined=timezone.now(), phone_num = 9876543210)
        # Create some items
        self.item1 = Item.objects.create(title="Test Item 1", description="Test description 1", price=9.99, seller = self.seller1.id)
        self.item2 = Item.objects.create(title="Test Item 2", description="Test description 2", price=19.99, seller = self.seller2.id)
        # Log the user in
        self.client = Client()
        self.client.login(username='testuser', password='testpass')
        # URL for add to cart
        self.add_to_cart_url = reverse('add_to_cart', args=[self.item1.id])
        # URL for view cart
        self.cart_detail_url = reverse('cart_detail')


class CartTestCase(TestCase):
    def setUp(self):
        self.seller1 = Seller.objects.create(name = "Test Name", date_joined=timezone.now(), phone_num = 1234567890)
        self.item = Item.objects.create(title="Test Item", price=10.00, seller = self.seller1)
        
    def test_add_to_cart(self):
        self.client.get(reverse('add_to_cart', args=[self.item.id]))
        cart = self.client.session['cart']
        self.assertIn(str(self.item.id), cart)

    def test_checkout(self):
        self.client.get(reverse('add_to_cart', args=[self.item.id]))
        self.client.get(reverse('checkout'))
        self.item.refresh_from_db()
        self.assertTrue(self.item.is_sold)

    def test_remove_from_cart(self):
        # Simulate adding an item to the cart
        self.client.session['cart'] = {str(self.item.id): 1}
        self.client.session.save()

        # URL for removing item from cart
        remove_from_cart_url = reverse('remove_from_cart', args=[self.item.id])

        # Perform the removal
        self.client.get(remove_from_cart_url)

        # Retrieve the updated session cart
        cart = self.client.session.get('cart', {})

        # Assert the item is removed from the cart
        self.assertNotIn(str(self.item.id), cart)

        # After making the request to remove the item
        self.client.get(remove_from_cart_url)

        # Reload the session to get updated data
        session = self.client.session
        session.save()  # This forces the session to be saved
        cart = session.get('cart', {})


class ReviewFormTests(TestCase):

    def test_review_form_submission(self):
        # Data for the review form
        form_data = {
            'name': 'Test User',
            'comment': 'This is a test review.'
        }

        # Submitting the review form
        response = self.client.post(reverse('review_form'), form_data)

        # Check if the form submission redirects to the item list page
        self.assertRedirects(response, reverse('item_list'))

        # Check if the review was created
        self.assertEqual(Review.objects.count(), 1)
        review = Review.objects.first()
        self.assertEqual(review.name, 'Test User')
        self.assertEqual(review.comment, 'This is a test review.')

class ItemListPageTests(TestCase):

    def setUp(self):
        # Create some test reviews
        Review.objects.create(name='User 1', comment='Comment 1')
        Review.objects.create(name='User 2', comment='Comment 2')

    def test_display_reviews_on_item_list_page(self):
        # Request the item list page
        response = self.client.get(reverse('item_list'))

        # Check if the page contains the reviews
        self.assertContains(response, 'Comment 1')
        self.assertContains(response, 'Comment 2')
        self.assertContains(response, 'User 1')
        self.assertContains(response, 'User 2')

class SellerFormTest(TestCase):

    def test_item_creation(self):
        #Check if the Seller was created
        seller = Seller.objects.create(name = "Test Name", date_joined=timezone.now(), phone_num = 1234567890)
        self.assertEqual(seller.name, "Test Name")
        self.assertEqual(seller.phone_num, 1234567890)


class ItemFormTest(TestCase):


    def test_form_validity(self):
        #Check if SellerForm is valid
        form_data = {'name': 'Test Name', 'date_joined': timezone.now(), 'phone_num': 1234567890}
        form = SellerForm(data=form_data)
        self.assertTrue(form.is_valid())


    def test_form_saves_seller(self):
        #Check if SellerForm saves the Seller to database
        form_data = {'name': 'Test Name', 'date_joined': timezone.now(), 'phone_num': 1234567890}
        form = SellerForm(data=form_data)
        if form.is_valid():
            new_seller = form.save() 
            self.assertEqual(Seller.objects.count(), 1)
            self.assertEqual(new_seller.name, 'Test Name')
            self.assertEqual(new_seller.phone_num, 1234567890)
