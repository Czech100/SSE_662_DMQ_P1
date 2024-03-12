from django.shortcuts import redirect
from .models import Item

class CheckoutProcess:
    def __init__(self, cart_manager):
        self.cart_manager = cart_manager
    
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


class CartManager:
    def __init__(self, session):
        self.session = session
        self.cart = session.get('cart', {})

    def add_item(self, item_id):
        self.cart[str(item_id)] = self.cart.get(str(item_id), 0) + 1
        self.update_session()

    def remove_item(self, item_id):
        if str(item_id) in self.cart:
            del self.cart[str(item_id)]
            self.update_session()

    def update(self, item_id, action='add'):
        if action == 'add':
            self.add_item(item_id)
        elif action == 'remove':
            self.remove_item(item_id)
        # Additional actions can be handled here if needed

    def get_items(self):
        return self.cart

    def clear_cart(self):
        self.cart = {}
        self.update_session()

    def checkout(request):
        checkout_process = CheckoutProcess(CartManager(request.session))
        checkout_process.execute()
        return redirect('item_list')

    def update_session(self):
        self.session['cart'] = self.cart
        self.session.modified = True
