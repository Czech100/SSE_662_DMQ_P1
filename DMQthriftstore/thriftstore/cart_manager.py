from django.shortcuts import redirect
from .models import Item
from decimal import Decimal


class CheckoutStrategy:
    def process_checkout(self, cart_manager):
        raise NotImplementedError("Subclasses must implement the process_checkout method.")

class StandardCheckout(CheckoutStrategy):
    def process_checkout(self, cart_manager):
        item_ids = cart_manager.get_items().keys()
        items = Item.objects.filter(id__in=item_ids, is_sold=False)
        for item in items:
            item.is_sold = True
            item.save()
        cart_manager.clear_cart()

class DiscountedCheckout(CheckoutStrategy):
    def process_checkout(self, cart_manager):
        item_ids = cart_manager.get_items().keys()
        items = Item.objects.filter(id__in=item_ids, is_sold=False)
        
        total_discount = Decimal('0.0')  # Initialize total discount

        for item in items:
            if item.category == 'CLOTHING':  
                og_price = item.price 
                discount = item.price * Decimal('0.2')  # Calculate 20% discount
                total_discount += discount
                item.price -= discount  # Apply discount
                item.is_sold = True
                item.save()
                print(f"Item {item.title} sold for {item.price} after a 20% discount. Original price was {og_price}.")
            else:
                item.is_sold = True
                item.save()
                print(f"Item {item.title} sold for {item.price} with no disocunt.")
        
        cart_manager.clear_cart()

        # Optionally, return total discount or other relevant information
        return total_discount


# Class to handle the checkout process
class CheckoutProcess:
    def __init__(self, cart_manager,checkout_strategy: CheckoutStrategy):
        self.cart_manager = cart_manager  # An instance of CartManager to manage cart operations
        self.checkout_strategy = checkout_strategy  # The strategy to apply during checkout
    
    def execute(self):
        self.checkout_strategy.process_checkout(self.cart_manager)

# Class to manage shopping cart operations
class CartManager:
    def __init__(self, session):
        self.session = session  # The current user session
        self.cart = session.get('cart', {})  # Retrieve the cart from the session, or initialize it if not present
        if self.cart:
            self.state = ItemState(self)
        else:
            self.state = EmptyState(self)

    def add_item(self, item_id):
        # Add an item to the cart or increase its quantity if already present
        self.state.add_item(item_id)
        self.update_session()
        self.state = ItemState(self)

    def remove_item(self, item_id):
        # Remove an item from the cart if it exists
        self.state.remove_item(item_id)
        self.update_session()
        if not self.cart:
            self.state = EmptyState(self)
        else:
            self.state = ItemState(self)

    def update(self, item_id, action='add'):
        # Update the cart by adding or removing an item
        if action == 'add':
            self.add_item(item_id)
        elif action == 'remove':
            self.remove_item(item_id)
        # Additional actions can be handled here if needed

    def get_items(self):
        # Return the items in the cart
        return self.state.get_items()

    def clear_cart(self):
        # Clear all items from the cart
        self.state.clear_cart()
        self.state = EmptyState(self)

    def update_session(self):
        # Update the session with the current state of the cart
        self.session['cart'] = self.cart
        self.session.modified = True

class State:
    def __init__(self, cart_manager):
        self.cart_manager = cart_manager

    def add_item(self, item_id):
        # Add an item to the cart or increase its quantity if already present
        pass

    def remove_item(self, item_id):
        # Remove an item from the cart if it exists
        pass

    def get_items(self):
        pass

    def clear_cart(self):
        pass


class EmptyState(State):
    def __init__(self, cart_manager):
        super().__init__(cart_manager)

    def add_item(self, item_id):
        # Add an item to the cart or increase its quantity if already present
        self.cart_manager.cart[str(item_id)] = self.cart_manager.cart.get(str(item_id), 0) + 1
        self.cart_manager.update_session()

    def remove_item(self, item_id):
        # Remove an item from the cart if it exists
        raise KeyError("Cart is empty!")

    def get_items(self):
        return self.cart_manager.cart

    def clear_cart(self):
        pass

class ItemState(State):
    def __init__(self, cart_manager):
        super().__init__(cart_manager)
        
    def add_item(self, item_id):
        # Add an item to the cart or increase its quantity if already present
        self.cart_manager.cart[str(item_id)] = self.cart_manager.cart.get(str(item_id), 0) + 1
        self.cart_manager.update_session()

    def remove_item(self, item_id):
        # Remove an item from the cart if it exists
        if str(item_id) in self.cart_manager.cart:
            del self.cart_manager.cart[str(item_id)]
            self.cart_manager.update_session()

    def get_items(self):
        return self.cart_manager.cart
    
    def clear_cart(self):
        self.cart_manager.cart = {}
        self.cart_manager.update_session()


class CheckOutState(State):
    def __init__(self, cart_manager, session):
        super().__init__(cart_manager, session)
        
    def add_item(self, item_id):
        # Add an item to the cart or increase its quantity if already present
        pass

    def remove_item(self, item_id):
        # Remove an item from the cart if it exists
        pass

    def get_items(self):
        pass

    def clear_cart(self):
        self.cart_manager.cart = {}
        self.cart_manager.update_session()
