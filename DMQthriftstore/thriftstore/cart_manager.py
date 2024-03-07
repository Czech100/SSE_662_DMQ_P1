from .models import Item


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

    def checkout(self):
        Item.objects.filter(id__in=self.cart.keys(), is_sold=False).update(is_sold=True)
        self.clear_cart()

    def update_session(self):
        self.session['cart'] = self.cart
        self.session.modified = True
