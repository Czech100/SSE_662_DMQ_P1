from django.test import TestCase, Client
from .models import Item, Review, Seller
from .forms import ItemForm, ReviewForm, SellerForm
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User


# Create your tests here.

class SellerFactory: #Creates a seller with default values if there are no arguments. Used to reduce redundant code of set ups.
    @staticmethod
    def create_seller(**kwargs):
        defaults = {
            'name': 'Default Seller Name',
            'date_joined': timezone.now(),
            'phone_num': 1234567890,
        }
        defaults.update(kwargs)
        return Seller.objects.create(**defaults)
    

class ItemFactory: #Creates an item with default values if there are no arguments. Used to reduce redundant code of set ups.
    @staticmethod
    def create_item(seller=None, **kwargs):
        if seller is None:
            seller = SellerFactory.create_seller()
        defaults = {
            'title': 'Default Item Title',
            'description': 'Default item description',
            'price': 9.99,
            'category': 'CLOTHING',
            'seller': seller,
        }
        defaults.update(kwargs)
        return Item.objects.create(**defaults)
    

class ItemModelTest(TestCase): #Tests that item creation is successful.
    def setUp(self):
        self.seller1 = SellerFactory.create_seller()

    def test_item_creation(self):
        item = ItemFactory.create_item(seller=self.seller1, title="Test Item", description="Just a test item.", price=9.99, category="CLOTHING")
        self.assertEqual(item.title, "Test Item")
        self.assertEqual(item.description, "Just a test item.")
        self.assertEqual(item.price, 9.99)
        self.assertEqual(item.seller.id, self.seller1.id)
        self.assertEqual(item.category, "CLOTHING")


class ItemFormTest(TestCase): #Tests that item is valid after creation and that the item saves correctly.
    def setUp(self):
        self.seller1 = SellerFactory.create_seller(name = "Test Name", date_joined=timezone.now(), phone_num = 1234567890)

    def test_form_validity(self):
        form_data = {'title': 'Test Item', 'description': 'A test item', 'price': 9.99, 'seller': self.seller1, 'category':'CLOTHING'}
        form = ItemForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_saves_item(self):
        form_data = {'title': 'Test Item', 'description': 'A test item', 'price': 9.99, 'seller': self.seller1, 'category':'CLOTHING'}
        form = ItemForm(data=form_data)
        if form.is_valid():
            new_item = form.save()
            self.assertEqual(Item.objects.count(), 1)
            self.assertEqual(new_item.title, 'Test Item')


class AddItemViewTest(TestCase): #Tests that the view renders the form correctly, and the item saves correctly with POST request.
    def setUp(self):
        self.seller1 = SellerFactory.create_seller(name = "Test Name", date_joined=timezone.now(), phone_num = 1234567890)

    def test_view_renders_item_form(self):
        response = self.client.get(reverse('add_item'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        self.assertIsInstance(response.context['item_form'], ItemForm)
        self.assertIsInstance(response.context['seller_form'], SellerForm)


    def test_view_saves_item_with_post_request(self):
        data = {
        'title': 'Test Item', 
        'description': 'A test item', 
        'price': 9.99, 
        'name': 'Test Name',
        'date_joined': timezone.now(),
        'phone_num': 1234567890,
        'category':'CLOTHING'
        }
        self.client.post(reverse('add_item'), data)
        self.assertEqual(Item.objects.count(), 1)


class AddItemTemplateTest(TestCase): #Tests that the add item template contains all fields. 
    def test_template_displays_form_fields(self):
        response = self.client.get(reverse('add_item'))
        self.assertContains(response, 'name="title"')
        self.assertContains(response, 'name="description"')
        self.assertContains(response, 'name="price"')
        self.assertContains(response, 'name="category')

class ItemBuyTest(TestCase): #Tests buying an item through a POST request.
    def setUp(self):
        self.seller1 = SellerFactory.create_seller(name="Test Name", phone_num=1234567890)
        self.item = ItemFactory.create_item(title="Test Item", description="Just a test item.", price=9.99, seller=self.seller1, category="CLOTHING")
    def test_buy_item(self):
        self.client.post(reverse('buy_item', args=(self.item.id,)))
        updated_item = Item.objects.get(id=self.item.id)
        
        self.assertTrue(updated_item.is_sold)

class RecentlySoldItemsTest(TestCase): #Tests that the recently sold items return from a GET request.
    def setUp(self):
        self.seller1 = SellerFactory.create_seller(name = "Test Name", date_joined=timezone.now(), phone_num = 1234567890)
       
    def test_recently_sold_items_display(self):
        sold_item = ItemFactory.create_item(title="Sold Item", description="A sold item", price=9.99, is_sold=True, sold_at=timezone.now(), seller = self.seller1, category="CLOTHING")
        response = self.client.get(reverse('item_list'))
        self.assertContains(response, sold_item.title)

class CartTests(TestCase): #Sets up for later cart test
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(username='testuser', password='testpass')
        # Create some sellers
        self.seller1 = SellerFactory.create_seller(name = "Test Name", date_joined=timezone.now(), phone_num = 1234567890)
        self.seller2 = SellerFactory.create_seller(name = "Test Name1", date_joined=timezone.now(), phone_num = 9876543210)
        # Create some items
        self.item1 = ItemFactory.create_item(title="Test Item 1", description="Test description 1", price=9.99, seller = self.seller1.id, category="CLOTHING")
        self.item2 = ItemFactory.create_item(title="Test Item 2", description="Test description 2", price=19.99, seller = self.seller2.id, category="CLOTHING")
        # Log the user in
        self.client = Client()
        self.client.login(username='testuser', password='testpass')
        # URL for add to cart
        self.add_to_cart_url = reverse('add_to_cart', args=[self.item1.id])
        # URL for view cart
        self.cart_detail_url = reverse('cart_detail')


class CartTestCase(TestCase):#Tests adding to the cart, checking out, and removing an item from the cart. 
    def setUp(self):
        self.seller1 = SellerFactory.create_seller(name = "Test Name", date_joined=timezone.now(), phone_num = 1234567890)
        self.item = ItemFactory.create_item(title="Test Item", price=10.00, seller = self.seller1, category="CLOTHING")
        
    def test_add_to_cart(self):
        self.client.get(reverse('add_to_cart', args=[self.item.id]))
        cart = self.client.session['cart']
        self.assertIn(str(self.item.id), cart)

    def test_checkout(self):
        # Add item to cart
        self.client.get(reverse('add_to_cart', args=[self.item.id]))
    
        # Simulate checkout process
        response = self.client.post(reverse('checkout'))

        # Check if checkout was successful (status code 302 indicates a redirect)
        self.assertEqual(response.status_code, 302)
    
        # Fetch the updated item from the database
        updated_item = Item.objects.get(id=self.item.id)
    
        # Check if the item is marked as sold
        self.assertTrue(updated_item.is_sold)



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


class ReviewFormTests(TestCase): #Tests that review forms POST correctly with the correct values.

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
        self.assertEqual(review.name, form_data.get('name')) 
        self.assertEqual(review.comment, form_data.get('comment'))

class ItemListPageTests(TestCase): #Tests that reviews display correctly.

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

class SellerFormTest(TestCase): #Tests that a seller was created correctly. 

    def test_item_creation(self):
        #Check if the Seller was created
        seller = SellerFactory.create_seller(name = "Test Name", date_joined=timezone.now(), phone_num = 1234567890)
        self.assertEqual(seller.name, "Test Name")
        self.assertEqual(seller.phone_num, 1234567890)


""" class ItemFormTest(TestCase): #Tests that a seller from is valid and that it saves correctly to database. 


    def test_form_validity(self):
        #Check if SellerForm is valid
        form_data = {'name': 'Test Name', 'date_joined': timezone.now(), 'phone_num': 1234567890}
        form = SellerForm(data=form_data)
        self.assertTrue(form.is_valid())


    def test_form_saves_seller(self):
        #Check if SellerForm saves the Seller to database
        form_data = {'name': 'Test Name', 'date_joined': timezone.now(), 'phone_num': '1234567890'}
        form = SellerForm(data=form_data)
        if form.is_valid():
            new_seller = form.save() 
            self.assertEqual(Seller.objects.count(), 1)
            self.assertEqual(new_seller.name, form_data.get('name'))
            self.assertEqual(new_seller.phone_num, form_data.get('phone_num')) """


class ItemFilterTests(TestCase): #Tests that the item filter is working correctly. 

    def setUp(self):
        # Create a seller
        self.seller1 = SellerFactory.create_seller(name="Test Seller", date_joined=timezone.now(), phone_num=1234567890)

        # Create items with different categories and sold status
        ItemFactory.create_item(title="Shirt", category="CLOTHING", is_sold=0, seller=self.seller1, price=19.99, description='A shirt')
        ItemFactory.create_item(title="Pants", category="CLOTHING", is_sold=1, seller=self.seller1, price=15.99, description='A pair of pants')
        ItemFactory.create_item(title="Laptop", category="ELECTRONICS", is_sold=0, seller=self.seller1, price=10.99, description='A laptop')
        ItemFactory.create_item(title="Chair", category="FURNITURE", is_sold=0, seller=self.seller1, price=18.99, description='A chair')

    def test_filter_by_category(self):
        response = self.client.get(reverse('test_filter') + '?category=ELECTRONICS')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Laptop")
        self.assertNotContains(response, "Pants")

    def test_no_filter(self):
        response = self.client.get(reverse('test_filter'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Shirt")
        self.assertNotContains(response, "Pants")


class DeleteReviewTest(TestCase): #Test the deletion and editing of reviews. 
    def setUp(self):
        self.review = Review.objects.create(name="Test Name", comment="Test Comment", created_at=timezone.now())

    def test_delete_entries(self):
        response = self.client.post(reverse('delete_review', args=[self.review.id]))
        self.assertRedirects(response, reverse('item_list'))

    def test_edit_review_view(self):
        # Get the edit review page
        response = self.client.get(reverse('edit_review', args=[self.review.id]))

        # Check that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check that the 'form' context variable is an instance of ReviewForm
        self.assertIsInstance(response.context['form'], ReviewForm)

    def test_submit_review_edit_view(self):
        # Get the edit review page
        response = self.client.get(reverse('submit_edited_review', args=[self.review.id]))

        # Check that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

         # Check that the 'review' context variable is an instance of Review
        self.assertTemplateUsed(response, 'review_form_edit.html')