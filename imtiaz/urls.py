from django.urls import path
from .views import *

urlpatterns = [
    path("", Index.as_view(), name='index'),

    path("shop/", Shop.as_view(), name='shop'),
    path('product/<slug:slug>/', ProductDetails.as_view(), name='product-details'),

    path("checkout/", checkout, name='checkout'),    
    path("process_checkout/", process_checkout, name='process_checkout'),    
    path("order_confirmation/<int:order_id>/", order_confirmation, name='order_confirmation'), 
    path('payment/<int:order_id>/<str:client_secret>/', payment, name='payment'),
    path('complete_payment/<int:order_id>/', complete_payment, name='complete_payment'),
    path('payment_success/', payment_success, name='payment_success'),

    path('add-to-cart/<slug:slug>/', add_to_cart, name='add_to_cart'),
    path('webhook/', stripe_webhook, name='stripe_webhook'),
    
    # Contact
    path('contact/', Contact.as_view(), name='contact'),
    # TransactionHistory
    path('transaction-history/', TransactionHistory.as_view(), name='transaction_history'),
    
    # Cart
    path("cart/", cart, name='cart'),
    path('cart/remove/<int:cart_id>/', remove_from_cart, name='remove-from-cart'),

    path('categories/', category_page, name='categories'),
    path('categories/<slug:slug>/', category_detail_page, name='category-detail'),

    # register 
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),

    path("register/", register, name='register'),

]
