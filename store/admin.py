from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

# admin.site.disable_action('delete_selected')

# register the models so the admin can manipulate them
class OrderItemInlineAdmin(admin.StackedInline):
    model = OrderItem
    # readonly_fields = ('product', 'order', 'quantity', 'price_per_unit', 'created_at', 'updated_at')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('ref', 'user', 'status', 'shipping_address', 'created_at')
    list_filter = ('status',)
    search_fields = ['ref', 'user__username', 'user__email', 'user__first_name',
     'user__last_name', 'status'
    ]
    ordering = ('-created_at', )
    # date_hierarchy = 'created_at'
    # readonly_fields = ('user', 'ref', 'deliver_date', 'shipping_address', 'created_at', 'updated_at')
    readonly_fields = ('ref',)
    actions = ('change_order_status_to_processing', 'change_order_status_to_pending', 'cancel_orders')
    inlines = [
        OrderItemInlineAdmin,
    ]

    def change_order_status_to_processing(self, request, queryset):
        queryset1 = queryset.exclude(status='cancelled').exclude(status='delivered')
        rows_updated = queryset1.update(status='processing')
        if rows_updated == 1:
            message_bit = "1 order's status was"
        else:
            message_bit = "%s orders' status were" % rows_updated
        self.message_user(request, "%s successfully changed to 'processing'." % message_bit)

    def change_order_status_to_pending(self, request, queryset):
        queryset1 = queryset.exclude(status='cancelled').exclude(status='delivered')
        rows_updated = queryset1.update(status='pending')
        if rows_updated == 1:
            message_bit = "1 order's status was"
        else:
            message_bit = "%s orders' status were" % rows_updated
        self.message_user(request, "%s successfully changed to 'processing'." % message_bit)

    def cancel_orders(self, request, queryset):
        queryset1 = queryset.exclude(status='cancelled').exclude(status='delivered')
        rows_updated = queryset1.update(status='cancelled')
        if rows_updated == 1:
            message_bit = "1 order was"
        else:
            message_bit = "%s orders were" % rows_updated
        self.message_user(request, "%s successfully cancelled. please state the reasons individually" % message_bit)

    change_order_status_to_processing.short_description = "Change the selected orders' status to 'processing'"
    change_order_status_to_pending.short_description = "Change the selected orders' status to 'pending'"
    cancel_orders.short_description = "Cancel the selected orders"


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'order', 'quantity', 'price_per_unit', 'created_at')
    list_filter = ('order__status', 'product__gender', 'product__brand__name', 'product__category__name' )
    search_fields = ['order__status', 'order__user__email', 'order__user__first_name', 'order__user__last_name']
    ordering = ('-created_at', )
    # date_hierarchy = 'created_at'
    # readonly_fields = ('product', 'order', 'quantity', 'price_per_unit', 'created_at', 'updated_at')


class ProductImageInlineAdmin(admin.StackedInline):
    model = ProductImage

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'admin', 'gender', 'brand', 'size', 'colour', 'orders_count', 'num_deliveries', 'quantity', 'price_per_unit', 'created_at')
    list_filter = ('gender', 'size', 'colour', 'brand__name')
    search_fields = ('name', 'gender', 'size', 'colour', 'category__name', 'brand__name', 'price_per_unit')
    # readonly_fields = ('created_at', 'updated_at', 'orders_count', 'num_deliveries')
    ordering = ('-created_at', )
    inlines = [
        ProductImageInlineAdmin,
    ]

class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('address', 'user', 'zip_code', 'city', 'state', 'created_at')
    list_filter = ('state', )
    search_fields = ('zip_code', 'address', 'city', 'state', 'user__username', 'user__email')
    # readonly_fields = ('address', 'user', 'zip_code', 'city', 'state', 'is_default',
        # 'country', 'created_at', 'updated_at'
    # )
    ordering = ('-created_at', )

admin.site.register(User, UserAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage)
admin.site.register(Brand)
admin.site.register(ProductCategory)
admin.site.register(Wish)
admin.site.register(Cart)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(ShippingAddress, ShippingAddressAdmin)
