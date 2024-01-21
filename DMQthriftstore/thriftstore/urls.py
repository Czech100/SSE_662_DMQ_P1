from django.urls import path
from . import views
from .views import remove_from_cart, review_form

urlpatterns = [
    path('', views.item_list, name='item_list'),
    path('add/', views.add_item, name='add_item'),
    path('buy/<int:item_id>/', views.buy_item, name='buy_item'),
    path('add_to_cart/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('checkout/', views.checkout, name='checkout'),
    path('remove_from_cart/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
    path('leave_review/', views.review_form, name='review_form'),
    path('submit_edit_review/<int:review_id>/', views.submit_review_edit, name='submit_edit_review'),
    path('edit_review/<int:review_id>/', views.edit_review, name='edit_review'),
    path('delete_review/<int:review_id>/', views.delete_review, name='delete_review'),
    path('test_filter/', views.test_filter, name='test_filter'),
]