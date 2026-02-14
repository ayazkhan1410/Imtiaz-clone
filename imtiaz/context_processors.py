from .models import Cart
from .models import Category

def cart_context(request):
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user, is_ordered=False)
        total_price = sum(item.total_price for item in cart_items)
        total_quantity = sum(item.quantity for item in cart_items)
    else:
        cart_items = []
        total_price = 0
        total_quantity = 0

    return {
        'cart_items': cart_items,
        'cart_total_price': total_price,
        'cart_total_quantity': total_quantity
    }

def category_context(request):
    categories = Category.objects.all()[0:4]
    return {
        "categories": categories
    }