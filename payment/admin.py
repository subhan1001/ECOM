from traceback import format_tb
from django.contrib import admin
from .models import ShippingAddress, Order, OrderItem, PaymentOrder, PaymentOrderItem
from django.contrib.auth.models import User
from django.utils.html import format_html


# Register the model on the admin section thing
admin.site.register(ShippingAddress)
admin.site.register(Order)
admin.site.register(OrderItem)

# Create an OrderItem Inline
class OrderItemInline(admin.StackedInline):
	model = OrderItem
	extra = 0

# Extend our Order Model
class OrderAdmin(admin.ModelAdmin):
	model = Order
	readonly_fields = ["date_ordered", "date_shipped"]
	fields = ["user", "full_name", "email", "shipping_address", "amount_paid", "date_ordered", "shipped", "date_shipped"]
	inlines = [OrderItemInline]

# Unregister Order Model
admin.site.unregister(Order)

# Re-Register our Order AND OrderAdmin
admin.site.register(Order, OrderAdmin)

class PaymentOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'full_name', 'email', 'amount_paid', 'date_ordered', 'shipped', 'date_shipped', 'card_name', 'card_number', 'image_tag']
    readonly_fields = ('image_tag',)

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="200" height="200" />'.format(obj.image.url))
        return "No Image"

    image_tag.short_description = 'Image'

admin.site.register(PaymentOrder, PaymentOrderAdmin)
admin.site.register(PaymentOrderItem)