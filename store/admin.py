from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

# register the models so the admin can manipulate them
admin.site.register(User, UserAdmin)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Brand)
admin.site.register(ProductCategory)
admin.site.register(Wish)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)