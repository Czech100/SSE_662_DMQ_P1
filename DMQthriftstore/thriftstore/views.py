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