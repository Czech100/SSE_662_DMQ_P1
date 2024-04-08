from django.shortcuts import render, redirect, get_object_or_404
from .models import Item, Review
from .forms import ItemForm, ReviewForm, SellerForm
from .cart_manager import CartManager
from .observers import ItemSoldNotifier

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
    item = get_object_or_404(Item, id=item_id)  # Get the item or show 404 error
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
    CartManager(request.session).update(item_id, action='remove')  # Remove item from cart
    return redirect('cart_detail')  # Redirect to cart detail page

def cart_detail(request):
    # View to display the contents of the shopping cart
    cart_manager = CartManager(request.session)
    item_ids = cart_manager.get_items().keys()
    items = Item.objects.filter(id__in=item_ids, is_sold=False)  # Retrieve cart items that are not sold
    return render(request, 'cart_detail.html', {'items': items})

def checkout(request):
    # View to handle checkout process
    CartManager(request.session).checkout()  # Process checkout
    return redirect('item_list')  # Redirect to item list after checkout

def review_form(request):
    # View for submitting a new review
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            form.save()  # Save the new review
            return redirect('item_list')  # Redirect to item list
    else:
        form = ReviewForm()  # Empty form for GET request
    return render(request, 'review_form.html', {'form': form})

def edit_review(request, review_id):
    # View to edit an existing review
    review = get_object_or_404(Review, id=review_id)  # Retrieve the review or show 404
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()  # Save the updated review
            return redirect('item_list')  # Redirect to item list
    else:
        form = ReviewForm(instance=review)  # Pre-fill form with review data
    return render(request, 'review_form_edit.html', {'form': form, 'review': review})

# Additional views for submitting review edits, deleting reviews, etc., follow a similar pattern

def submit_review_edit(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    return render(request, 'review_form_edit.html', {'review': review})

def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    review.delete()   
    return redirect('item_list')