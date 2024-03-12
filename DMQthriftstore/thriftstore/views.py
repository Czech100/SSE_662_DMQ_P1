from django.shortcuts import render, redirect, get_object_or_404
from .models import Item, Review
from .forms import ItemForm, ReviewForm, SellerForm
from .cart_manager import CartManager

# Create your views here.


def get_filtered_items(category=None):
    if category:
        return Item.objects.filter(category=category, is_sold=False)
    return Item.objects.filter(is_sold=False)


def item_list(request):
    reviews = Review.objects.all().order_by('-created_at')
    
    # Filter items that are not sold
    
    
    recently_sold_items = Item.objects.filter(is_sold=True).order_by('-sold_at')[:5]  # Adjust the number as needed

    category = request.GET.get('category')
    

    categories = Item.CATEGORY_CHOICES
    items = get_filtered_items(category)

    return render(request, 'item_list.html', {
        'items': items,
        'recently_sold_items': recently_sold_items,
        'reviews': reviews,
        'categories': categories, 
    })

def test_filter(request):
    # Filter items that are not sold
    available_items = Item.objects.filter(is_sold=0)

    category = request.GET.get('category')

    # Apply additional filters based on category
    if category:
        available_items = available_items.filter(category=category)

    categories = Item.CATEGORY_CHOICES

    return render(request, 'test_filter.html', {
        'items': available_items,
        'categories': categories,
    })

def add_item(request):
    if request.method == "POST":
        item_form = ItemForm(request.POST)
        seller_form = SellerForm(request.POST)

        if item_form.is_valid() and seller_form.is_valid():
            seller = seller_form.save()  # Create and save the Seller instance
            item = item_form.save(commit=False)  # Create the Item instance but don't save it yet
            item.seller = seller  # Associate the item with the seller
            item.save()  # Save the Item instance with the seller reference

            return redirect('item_list')  # Redirect to the list view
    else:
        item_form = ItemForm()
        seller_form = SellerForm()

    return render(request, 'add_item.html', {'item_form': item_form, 'seller_form': seller_form})


def buy_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    mark_item_as_sold(item)
    return redirect('item_list')

def mark_item_as_sold(item):
    item.mark_as_sold()


def add_to_cart(request, item_id):
    CartManager(request.session).update(item_id, action='add')
    return redirect('item_list')

def remove_from_cart(request, item_id):
    CartManager(request.session).update(item_id, action='remove')
    return redirect('cart_detail')

def cart_detail(request):
    cart_manager = CartManager(request.session)
    item_ids = cart_manager.get_items().keys()
    items = Item.objects.filter(id__in=item_ids, is_sold=False)
    return render(request, 'cart_detail.html', {'items': items})

def checkout(request):
    CartManager(request.session).checkout()
    return redirect('item_list')

def review_form(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('item_list')
    else:
        form = ReviewForm()
    return render(request, 'review_form.html', {'form': form})

def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('item_list')
    else:
        form = ReviewForm(instance=review)

    return render(request, 'review_form_edit.html', {'form': form, 'review': review})

def submit_review_edit(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    return render(request, 'review_form_edit.html', {'review': review})

def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    review.delete()   
    return redirect('item_list')