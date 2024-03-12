from django.shortcuts import redirect
from .models import Item

# Class to handle the checkout process
class CheckoutProcess:
    def __init__(self, cart_manager):
        self.cart_manager = cart_manager  # An instance of CartManager to manage cart operations
    
    def execute(self):
        # Retrieve item instances based on IDs stored in the cart
        item_ids = self.cart_manager.get_items().keys()
        items = Item.objects.filter(id__in=item_ids, is_sold=False)
        
        # Mark each item as sold
        for item in items:
            item.is_sold = True
            item.save()
        
        # Clear the cart after marking items as sold
        self.cart_manager.clear_cart()

# Class to manage shopping cart operations
class CartManager:
    def __init__(self, session):
        self.session = session  # The current user session
        self.cart = session.get('cart', {})  # Retrieve the cart from the session, or initialize it if not present

    def add_item(self, item_id):
        # Add an item to the cart or increase its quantity if already present
        self.cart[str(item_id)] = self.cart.get(str(item_id), 0) + 1
        self.update_session()

    def remove_item(self, item_id):
        # Remove an item from the cart if it exists
        if str(item_id) in self.cart:
            del self.cart[str(item_id)]
            self.update_session()

    def update(self, item_id, action='add'):
        # Update the cart by adding or removing an item
        if action == 'add':
            self.add_item(item_id)
        elif action == 'remove':
            self.remove_item(item_id)
        # Additional actions can be handled here if needed

    def get_items(self):
        # Return the items in the cart
        return self.cart

    def clear_cart(self):
        # Clear all items from the cart
        self.cart = {}
        self.update_session()

    def checkout(request):
        # Process checkout: mark items as sold and clear the cart
        checkout_process = CheckoutProcess(CartManager(request.session))
        checkout_process.execute()
        return redirect('item_list')  # Redirect to the item list page after checkout

    def update_session(self):
        # Update the session with the current state of the cart
        self.session['cart'] = self.cart
        self.session.modified = True

