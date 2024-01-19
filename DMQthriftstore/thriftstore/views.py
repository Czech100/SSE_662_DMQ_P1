from django.shortcuts import render, redirect, get_object_or_404
from .models import Item
from .forms import ItemForm


# Create your views here.

def item_list(request):
    available_items = Item.objects.filter(is_sold=False)
    recently_sold_items = Item.objects.filter(is_sold=True).order_by('-sold_at')[:5]  # Adjust the number as needed
    return render(request, 'item_list.html', {
        'items': available_items,
        'recently_sold_items': recently_sold_items
    })

def add_item(request):
    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('item_list')  # Redirect to the list view
    else:
        form = ItemForm()
    return render(request, 'add_item.html', {'form': form})

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

