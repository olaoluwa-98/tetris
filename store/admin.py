from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

# admin.site.disable_action('delete_selected')

# register the models so the admin can manipulate them
class OrderAdmin(admin.ModelAdmin):
    list_display = ('ref', 'user', 'status', 'created_at')
    list_filter = ('status', 'user__username')
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    ordering = ('created_at', )
    # date_hierarchy = 'created_at'
    exclude = ('created_at', 'updated_at', 'ref')
    actions = ('change_order_status_to_processing', 'change_order_status_to_delivered', 'cancel_orders')

    def change_order_status_to_processing(self, request, queryset):
        rows_updated = queryset.update(status='processing')
        if rows_updated == 1:
            message_bit = "1 order's status was"
        else:
            message_bit = "%s orders' status were" % rows_updated
        self.message_user(request, "%s successfully changed to 'processing'." % message_bit)

    def change_order_status_to_delivered(self, request, queryset):
        rows_updated = queryset.update(status='delivered')
        if rows_updated == 1:
            message_bit = "1 order's status was"
        else:
            message_bit = "%s orders' status were" % rows_updated
        self.message_user(request, "%s successfully changed to 'delivered'." % message_bit)

    def cancel_orders(self, request, queryset):
        rows_updated = queryset.update(status='cancelled')
        if rows_updated == 1:
            message_bit = "1 order was"
        else:
            message_bit = "%s orders were" % rows_updated
        self.message_user(request, "%s successfully cancelled." % message_bit)

    change_order_status_to_processing.short_description = "Change the selected orders' status to 'processing'"
    change_order_status_to_delivered.short_description = "Change the selected orders' status to 'delivered'"
    cancel_orders.short_description = "Cancel the selected orders"


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'order', 'quantity', 'price_per_unit', 'created_at')
    list_filter = ('order__status', 'product__gender', 'product__brand__name', 'product__category__name' )
    search_fields = ['order__status', 'order__user__email', 'order__user__first_name', 'order__user__last_name']
    ordering = ('created_at', )
    # date_hierarchy = 'created_at'
    exclude = ('created_at', 'updated_at',)


admin.site.register(User, UserAdmin)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Brand)
admin.site.register(ProductCategory)
admin.site.register(Wish)
admin.site.register(Cart)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(ShippingAddress)
