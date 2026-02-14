from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.utils.text import slugify

class MyUserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            username=username,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    username = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="category", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            unique_slug = self.slug
            num = 1
            while Category.objects.filter(slug = unique_slug).exists():
                unique_slug = f"{self.slug } - {num}"
                num +=1
                self.slug = unique_slug
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.slug}"


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="product", blank=True)
    orignal_price = models.PositiveIntegerField(default=0)
    discount_percentage = models.PositiveIntegerField(default=0)
    discounted_price = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    in_stock = models.IntegerField(default=1)
    most_wanted = models.BooleanField(default=False)
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_discounted_price(self):
        # Calculate discounted price based on percentage
        discount_amount = (float(self.discount_percentage) / 100) * float(self.orignal_price)
        discounted_price = float(self.orignal_price) - discount_amount
        return round(discounted_price, 2)

    def formatted_price(self):
        return "{:.2f}".format(self.orignal_price)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            unique_slug = self.slug
            num = 1
            while Product.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{self.slug} - {num}"
                num += 1
                self.slug = unique_slug
        super(Product, self).save(*args, **kwargs)


    def __str__(self):
        return self.name  



class FeatureProductImage(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='feature_product_images')
    image1 = models.ImageField(upload_to='feature_product_images/', blank=True, null=True)
    image2 = models.ImageField(upload_to='feature_product_images/', blank=True, null=True)
    image3 = models.ImageField(upload_to='feature_product_images/', blank=True, null=True)

    def _str_(self):
        return self.product.name



class Cart(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='user_carts')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_carts')
    quantity = models.PositiveIntegerField(default=1)
    is_ordered = models.BooleanField(default=False)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def mark_as_ordered_or_deleted(self):
            if not self.is_ordered:
                self.is_ordered = True
                self.save()

    def __str__(self):
        return self.user.email

    def total_items(self):
        total_items = 0
        cart_items = Cart.objects.filter(user=self, is_ordered=False)
        for item in cart_items:
            total_items += item.quantity
        return total_items
    

class ShippingAddress(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='shipping_address')
    name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    company_name = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField()
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    phone_number = models.CharField(max_length=255)
    order_note = models.TextField(null=True, blank=True)
    ship_to_different_address = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} {self.last_name} - {self.city}, {self.state}"




class Order(models.Model):
    PENDING = 'pending'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
    ]

    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name="orders")
    shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=255, blank=True)
    payment_status = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.email}"

    def mark_as_completed(self):
        self.status = self.COMPLETED
        self.save()

    def mark_as_cancelled(self):
        self.status = self.CANCELLED
        self.save()

    def update_payment_status(self, status):
        self.payment_status = status
        self.save()

    def calculate_total(self):
        cart_items = Cart.objects.filter(user=self.user, is_ordered=True)
        total = sum(item.total_price for item in cart_items)
        self.total_price = total
        self.save()
