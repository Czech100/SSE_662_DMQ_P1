from django.shortcuts import render, redirect, get_object_or_404
from .models import Item, Review
from .forms import ItemForm, ReviewForm, SellerForm


# Create your views here.

def item_list(request):
    reviews = Review.objects.all().order_by('-created_at')
    
    # Filter items that are not sold
    
    
    recently_sold_items = Item.objects.filter(is_sold=True).order_by('-sold_at')[:5]  # Adjust the number as needed

    category = request.GET.get('category')
    
    # Apply additional filters based on category
    if category:
        available_items = Item.objects.filter(category=category, is_sold=False)
    else:
        available_items = Item.objects.filter(is_sold=False)

    categories = Item.CATEGORY_CHOICES
    items = available_items

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
    item.mark_as_sold()
    
    return redirect('item_list')


def add_to_cart(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    cart = request.session.get('cart', {})
    
    # Add item to cart or update quantity
    if item_id in cart:
        cart[item_id] += 1
    else:
        cart[item_id] = 1
    
    request.session['cart'] = cart
    return redirect('item_list')

def cart_detail(request):
    item_ids = request.session.get('cart', {}).keys()
    items = Item.objects.filter(id__in=item_ids, is_sold=False)
    return render(request, 'cart_detail.html', {'items': items})

def checkout(request):
    cart = request.session.get('cart', {})
    
    if cart:
        items = Item.objects.filter(id__in=cart.keys(), is_sold=False)
        for item in items:
            item.mark_as_sold()
            item.save()
        del request.session['cart']  # Clear the cart after checkout
    
    return redirect('item_list')

def remove_from_cart(request, item_id):
    cart = request.session.get('cart', {})
    item_id_str = str(item_id)

    if item_id_str in cart:
        del cart[item_id_str]
        request.session['cart'] = cart

    return redirect('cart_detail')

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