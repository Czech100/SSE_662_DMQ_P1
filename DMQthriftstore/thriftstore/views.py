from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from .models import Item, Review
from .forms import ItemForm, ReviewForm, SellerForm
from .cart_manager import CartManager, StandardCheckout, CheckoutProcess, DiscountedCheckout
from .observers import ItemSoldNotifier
from .commands import EditReviewCommand, ReviewReciever, NewReviewCommand, Invoker

def get_filtered_items(category=None):
    # Retrieve items filtered by category if provided, and not sold
    if category:
        return Item.objects.filter(category=category, is_sold=False)
    return Item.objects.filter(is_sold=False)

def item_list(request):
    # View to display a list of items, filtering functionality, and recent reviews
    reviews = Review.objects.all().order_by('-created_at')  # Latest reviews first
    
    # Filter for recently sold items
    recently_sold_items = Item.objects.filter(is_sold=True).order_by('-sold_at')[:5]  # Last 5 sold items

    category = request.GET.get('category')  # Get category from request for filtering
    categories = Item.CATEGORY_CHOICES  # All available categories
    items = get_filtered_items(category)  # Filtered items based on the category

    # Render the item list page with the context containing items, categories, and reviews
    return render(request, 'item_list.html', {
        'items': items,
        'recently_sold_items': recently_sold_items,
        'reviews': reviews,
        'categories': categories, 
    })


def test_filter(request):
    category = request.GET.get('category')  # For example, getting a category query parameter from the request
    items = get_filtered_items(category=category)  # Reusing the existing filtering function
    
    # Render a template with the filtered items. You might need to create a specific template for this view.
    return render(request, 'test_filter.html', {'items': items})

def add_item(request):
    # View for adding a new item, handles both GET (form display) and POST (form submission)
    if request.method == "POST":
        item_form = ItemForm(request.POST)
        seller_form = SellerForm(request.POST)

        if item_form.is_valid() and seller_form.is_valid():
            seller = seller_form.save()  # Save seller information
            item = item_form.save(commit=False)  # Create item instance without saving
            item.seller = seller  # Link item with its seller
            item.save()  # Save the item to the database

            return redirect('item_list')  # Redirect to item list after saving
    else:
        item_form = ItemForm()  # Empty form for GET request
        seller_form = SellerForm()

    # Render the add item page with empty or prefilled forms
    return render(request, 'add_item.html', {'item_form': item_form, 'seller_form': seller_form})

def buy_item(request, item_id):
    # View to handle the buying of an item
    mark_item_as_sold(request, item_id)  # Mark the item as sold
    return redirect('item_list')  # Redirect to item list

def mark_item_as_sold(request, item_id):
    # Helper function to mark an item as sold
    item = get_object_or_404(Item, pk=item_id)
    sold_notifier = ItemSoldNotifier()
    item.attach_observer(sold_notifier)
    item.mark_as_sold()

def add_to_cart(request, item_id):
    # View to add an item to the shopping cart
    CartManager(request.session).update(item_id, action='add')  # Add item to cart
    return redirect('item_list')  # Redirect to item list

def remove_from_cart(request, item_id):
    # View to remove an item from the shopping cart
    cart_manager = CartManager(request.session)
    try:
        cart_manager.update(item_id, action='remove')  # Remove item from cart
    except KeyError as e:
        # Handle the case where the cart is empty
        return HttpResponse("Cart is empty!") 
    return redirect('cart_detail')  # Redirect to cart detail page

def cart_detail(request):
    # View to display the contents of the shopping cart
    cart_manager = CartManager(request.session)
    item_ids = cart_manager.get_items().keys()
    items = Item.objects.filter(id__in=item_ids, is_sold=False)  # Retrieve cart items that are not sold
    return render(request, 'cart_detail.html', {'items': items})

def checkout(request):
    if request.method == "POST":
        checkout_strategy = DiscountedCheckout()
        cart_manager = CartManager(request.session)
        checkout_process = CheckoutProcess(cart_manager, checkout_strategy)
        checkout_process.execute()

        item_ids = cart_manager.get_items().keys()
        items = Item.objects.filter(id__in=item_ids)
        items.update(is_sold=True)
        return redirect('item_list')
    else:
        return HttpResponse("GET request to checkout not supported")

def handle_review(request, review_id = None):
    review_handle = ReviewFacade(request, review_id)
    return review_handle.handle()

#Facade Pattern
class ReviewFacade:
    def __init__(self, request, review_id):
        self.request = request
        self.review_id = review_id
        if self.review_id == None and 'leave_review' in request.path:
            self.action = LeaveReview()
            return
        if 'edit_review' in request.path:
            self.action = EditReview()
            return
        if 'submit_edited_review' in request.path:
            self.action = SubmitEditReview()
            return
        if 'delete_review' in request.path:
            self.action = DeleteReview()
            return
        
    def handle(self):
        return self.action.handle_review(self.request, self.review_id) 

class LeaveReview:
    #Submit Review
    def handle_review(self, request, review_id):
        review_reciever = ReviewReciever()
        new_review_command = NewReviewCommand(review_reciever, request)
        invoker = Invoker()
        invoker.register_command("Create Review", new_review_command)
        form = invoker.execute("Create Review")
        if form == None: return redirect('item_list')
        return render(request, 'review_form.html', {'form': form})

class EditReview:
    #Edit Review
    def handle_review(self, request, review_id):
        review_reciever = ReviewReciever()
        edit_review_command = EditReviewCommand(review_reciever, request, review_id)
        invoker = Invoker()
        invoker.register_command("Edit Review", edit_review_command)
        form = invoker.execute("Edit Review")
        if form == None: return redirect('item_list')
        return render(request, 'review_form.html', {'form': form})

class SubmitEditReview:
    #Submit Edit Review
    def handle_review(self, request, review_id):
        review = get_object_or_404(Review, id=review_id)
        return render(request, 'review_form_edit.html', {'review': review})
    
class DeleteReview:
    #Delete Review
    def handle_review(self, request, review_id):
        review = get_object_or_404(Review, id=review_id)
        review.delete()   
        return redirect('item_list')