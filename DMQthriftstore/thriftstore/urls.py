from django.urls import path
from . import views
from .views import remove_from_cart

urlpatterns = [
    path('', views.item_list, name='item_list'),  # The home page, listing all items
    path('add/', views.add_item, name='add_item'),  # Page to add a new item
    path('buy/<int:item_id>/', views.buy_item, name='buy_item'),  # Endpoint to buy an item
    path('add_to_cart/<int:item_id>/', views.add_to_cart, name='add_to_cart'),  # Add an item to the shopping cart
    path('cart/', views.cart_detail, name='cart_detail'),  # View shopping cart details
    path('checkout/', views.checkout, name='checkout'),  # Checkout page to finalize purchase
    path('remove_from_cart/<int:item_id>/', remove_from_cart, name='remove_from_cart'),  # Remove an item from the cart
    path('leave_review/', views.handle_review, name='review_form'),  # Page to leave a review for an item
    path('submit_edited_review/<int:review_id>/', views.handle_review, name='submit_edited_review'),  # Submit an edited review
    path('edit_review/<int:review_id>/', views.handle_review, name='edit_review'),  # Page to edit a review
    path('delete_review/<int:review_id>/', views.handle_review, name='delete_review'),  # Endpoint to delete a review
    path('test_filter/', views.test_filter, name='test_filter'),  # A test page for filtering functionality
]
