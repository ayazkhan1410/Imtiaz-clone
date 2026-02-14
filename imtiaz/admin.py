from django.contrib import admin
from .models import *


@admin.register(MyUser)
class MyUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'is_admin')
    search_fields = ('email', 'username')
    
# Register Category model
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at', 'updated_at')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

# Register Product model
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'orignal_price', 'discount_percentage', 'description', 'is_available', 'in_stock', 'most_wanted')
    search_fields = ('name', 'category__name')
    list_filter = ('category', 'is_available')
    prepopulated_fields = {'slug': ('name',)}

# Register FeatureProductImage model
@admin.register(FeatureProductImage)
class FeatureProductImageAdmin(admin.ModelAdmin):
    list_display = ('product','image1','image2','image3')
    search_fields = ('product__name',)


# Register Cart model
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'is_ordered', 'total_price', 'created_at')
    search_fields = ('user__email', 'product__name')
    list_filter = ('is_ordered',)

# Register ShippingAddress model
@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('name', 'last_name', 'address', 'city', 'state', 'zip_code', 'email', 'phone_number')
    search_fields = ('email', 'phone_number', 'city', 'state')

from django.contrib import admin
from .models import Order

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'payment_status', 'total_price', 'created_at', 'updated_at')
    list_filter = ('status', 'payment_status')
    search_fields = ('user__email', 'status', 'payment_method')
    ordering = ('-created_at',)

    # Optionally, you can add actions to mark orders as completed or cancelled directly from the admin interface
    actions = ['mark_as_completed', 'mark_as_cancelled']

    def mark_as_completed(self, request, queryset):
        queryset.update(status=Order.COMPLETED)
        self.message_user(request, "Selected orders have been marked as completed.")
    
    def mark_as_cancelled(self, request, queryset):
        queryset.update(status=Order.CANCELLED)
        self.message_user(request, "Selected orders have been marked as cancelled.")
    
    mark_as_completed.short_description = "Mark selected orders as completed"
    mark_as_cancelled.short_description = "Mark selected orders as cancelled"

# Register the Order model with the custom admin class
admin.site.register(Order, OrderAdmin)
