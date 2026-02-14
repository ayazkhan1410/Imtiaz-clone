from django.shortcuts import render
from django.views import View
from .models import *
from datetime import timedelta
from django.utils import timezone

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.conf import settings
from django.http import JsonResponse
import stripe
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from stripe.error import SignatureVerificationError
from stripe.webhook import Webhook


class Index(View):

    def get(self, request):
        categories = Category.objects.all()

        context = {
            "categories": categories
        }
        return render(request, 'index.html', context)


class Shop(View):
    
    def get(self, request):
        categories = Category.objects.all()
        products = Product.objects.select_related('category').all()
        most_wanted = Product.objects.filter(most_wanted=True)
        print("MOST WANTED ====================", most_wanted)
        print("PRODUCT ====================", products)

        context = {
            "categories": categories,
            "products": products,
            "most_wanted": most_wanted
        }
        return render(request, 'shop.html', context)

class ProductDetails(View):
    
    def get(self, request, slug):
        product = Product.objects.filter(slug=slug).first()
        
        # Fetch the related FeatureProductImage for the product
        feature_images = FeatureProductImage.objects.filter(product=product).first()

        # Filtering Last Seven days products
        current_time = timezone.now()
        seven_days_ago = current_time - timedelta(days=7)
        latest_products = Product.objects.filter(created_at__gte=seven_days_ago)

        context = {
            "product": product,
            "feature_images": feature_images,
            "latest_products": latest_products
        }
        return render(request, 'detail-product.html', context)



@login_required
def add_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)

    if request.method == "POST":
        quantity = int(request.POST.get('quantity', 1))

        # Ensure quantity does not exceed available stock
        if quantity > product.in_stock:
            messages.error(request, "Not enough stock available.")
            return redirect('product-details', slug=product.slug)

        # Check if product already exists in the user's cart
        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product=product,
            is_ordered=False
        )

        # Update the cart item's quantity
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity

        # Calculate total price
        cart_item.total_price = cart_item.quantity * product.calculate_discounted_price()
        cart_item.save()

        messages.success(request, f"{product.name} has been added to your cart.")
        return redirect('product-details', slug=product.slug)

    return redirect('product-details', slug=product.slug)


def get_cart_data(request):
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user, is_ordered=False)
        total_price = sum(item.total_price for item in cart_items)
        total_quantity = sum(item.quantity for item in cart_items)
    else:
        cart_items = []
        total_price = 0
        total_quantity = 0

    return {'cart_items': cart_items, 'total_price': total_price, 'total_quantity': total_quantity}


def cart(request):
    cart_data = Cart.objects.filter(user=request.user, is_ordered=False)
    return render(request, "cart.html", {"cart_data": cart_data})

def remove_from_cart(request, cart_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(Cart, id=cart_id, user=request.user, is_ordered=False)
        cart_item.delete()
        return JsonResponse({'success': True, 'message': 'Item removed from cart successfully'})
    return JsonResponse({'success': False, 'message': 'Invalid request'})


stripe.api_key = settings.STRIPE_API_KEY

@login_required
def checkout(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user, is_ordered=False)

    if not cart_items:
        messages.error(request, "Your cart is empty.")
        return redirect('shop')

    total_price = sum(item.total_price for item in cart_items)

    shipping_cost = 200

    # Calculate total order amount
    total_amount = total_price + shipping_cost

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'shipping_cost': shipping_cost,
        'total_amount': total_amount,
    }
    
    return render(request, 'checkout.html', context)

from django.conf import settings
from django.http import JsonResponse
import stripe
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from stripe.error import SignatureVerificationError
from stripe.webhook import Webhook


stripe.api_key = settings.STRIPE_API_KEY
def update_order_payment_status(order, status):
    order.payment_status = status
    if status == 'succeeded':
        order.mark_as_completed()
    elif status == 'failed':
        order.mark_as_cancelled()
    order.save()

@csrf_exempt
def stripe_webhook(request):
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

    try:
        event = Webhook.construct_event(payload, sig_header, endpoint_secret)
    except (ValueError, SignatureVerificationError) as e:
        return JsonResponse({"error": str(e)}, status=400)

    # Handle the events
    if event["type"] == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        order_id = payment_intent.get("metadata", {}).get("order_id")  # Assuming you store `order_id` in metadata
        if order_id:
            from  imtiaz.models import Order  # Import your order model
            try:
                order = Order.objects.get(id=order_id)
                update_order_payment_status(order, "succeeded")
            except Order.DoesNotExist:
                return JsonResponse({"error": "Order not found"}, status=404)

    elif event["type"] == "payment_intent.payment_failed":
        payment_intent = event["data"]["object"]
        order_id = payment_intent.get("metadata", {}).get("order_id")
        if order_id:
            from models import Order
            try:
                order = Order.objects.get(id=order_id)
                update_order_payment_status(order, "failed")
            except Order.DoesNotExist:
                return JsonResponse({"error": "Order not found"}, status=404)

    return JsonResponse({"status": "success"}, status=200)


@login_required
def process_checkout(request):
    if request.method == 'POST':
        # Retrieve form data from the checkout form
        name = request.POST.get('name')
        last_name = request.POST.get('last_name')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        terms = request.POST.get('terms')

        # Get cart data
        user = request.user
        cart_items = Cart.objects.filter(user=user, is_ordered=False)

        if not cart_items:
            messages.error(request, "Your cart is empty.")
            return redirect('shop')  # Redirect to shop page if cart is empty

        # Create ShippingAddress
        shipping_address = ShippingAddress.objects.create(
            cart=cart_items.first(),  # Assuming the cart item is associated with this shipping address
            name=name,
            last_name=last_name,
            address=address,
            city=city,
            state=state,
            zip_code=zip_code,
            email=email,
            phone_number=phone_number,
        )

        # Create an Order
        order = Order.objects.create(
            user=user,
            shipping_address=shipping_address,
            total_price=0,  # Placeholder, will be updated after calculating total
        )

        # Calculate the total price and update the order
        order.calculate_total()

        # Mark cart items as ordered
        for item in cart_items:
            item.mark_as_ordered_or_deleted()

        # Now create the Stripe PaymentIntent
        total_amount = int((order.total_price) * 100)  # Convert to cents for Stripe

        payment_intent = stripe.PaymentIntent.create(
            amount=total_amount,
            currency='usd',
            metadata={'order_id': order.id},  # Pass the order ID here
        )

        # Redirect the user to the payment page with the payment intent's client secret and order id
        return redirect('payment', order_id=order.id, client_secret=payment_intent.client_secret)

    return redirect('checkout')


@login_required
def payment(request, order_id, client_secret):
    # Fetch the order and verify the user's access
    order = Order.objects.get(id=order_id)

    if order.user != request.user:
        messages.error(request, "You do not have permission to access this order.")
        return redirect('shop')

    # Provide the client secret to the frontend
    context = {
        'order_id': order.id,
        'client_secret': client_secret,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
    }

    return render(request, 'payment.html', context)


@login_required
def complete_payment(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        # Check if payment was successful (handle status, etc.)
        order.payment_status = 'Completed'
        order.save()
       

        # Redirect to a success page or show a success message
        return redirect('payment_success')

    except Order.DoesNotExist:
        return redirect('checkout')


@login_required
def payment_success(request):
    return render(request, 'payment_success.html')


def order_confirmation(request, order_id):
    order = Order.objects.get(id=order_id)
    context = {
        'order': order
    }
    return render(request, 'order_confirmation.html', context)


class Contact(View):

    def get(self, request):
        return render(request, 'contact.html')

from django.core.paginator import Paginator

class TransactionHistory(View):

    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        paginator = Paginator(orders, 5)  # Show 5 orders per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'orders': orders,
            'page_obj': page_obj
        }
        return render(request, 'transaction.html', context)
    


def category_page(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
    }
    return render(request, 'category.html', context)

def category_detail_page(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.all()  # Use the related_name defined in the Product model
    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'category_detail.html', context)




# views.py
from django.shortcuts import render, redirect
from .forms import RegisterForm, LoginForm
from .models import MyUser
from django.contrib import messages
from django.contrib.auth import authenticate, login

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            messages.success(request, "Registration successful. You can now log in.")
            return redirect("login")  # Redirect to the login page after successful registration
    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import LoginForm
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .forms import LoginForm
from django.contrib.auth.views import LoginView

class CustomLoginView(LoginView):
    template_name = 'login.html'

    def get_success_url(self):
        # Redirect to a custom URL after successful login
        return self.request.GET.get('next', '/')
    


from django.shortcuts import redirect
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View

class CustomLogoutView(View):
    def get(self, request, *args, **kwargs):
        # Log the user out
        logout(request)
        return redirect('index')