import calendar
from datetime import datetime, timedelta
from .models import Brand, Product, ProductCategory
from django.db.models import Q

# This class preprocesses and returns different collections
class Collections:
    def popular_brands(self, limit):
        brands = Brand.objects.filter()[:limit]
        popular_brands = sorted(
            brands,
            key=lambda b: (86400 * b.get_wishes().count() \
            + 86400 * b.get_orders().count()\
            + 86400 * b.get_carts().count())
            + calendar.timegm(b.created_at.utctimetuple()),
            reverse=True
        )
        return popular_brands

    def popular_products(self, limit):
        # threshold of 30 days
        post_time_threshold = datetime.now() - timedelta(days=30)

        # select products available in stock
        products = Product.objects.filter(quantity__gte=1, created_at__gte=post_time_threshold)
        popular_products = sorted(
            products,
            key=lambda p: (86400 * p.wishes.count() \
            + 86400 * p.order_items.count() \
            + 86400 * p.cart.count()) \
            + calendar.timegm(p.created_at.utctimetuple()),
            reverse=True
        )
        return popular_products[:limit]

    def related_products(self, product, limit=5):
        brand_name = ''
        cat_name = ''
        if product.brand:
            brand_name = product.brand.name
        if product.category:
            cat_name = product.brand.name
        related_products = Product.objects.filter(
            Q(name__icontains=product.name) |\
            Q(gender__icontains=product.gender) | Q(colour__icontains=product.colour) |\
            Q(brand__name__istartswith=brand_name) | \
            Q(category__name__istartswith=cat_name) |\
            Q(size__icontains=product.size) | Q(price_per_unit__icontains=product.price_per_unit)
        ).exclude(pk=product.pk).order_by('-created_at')
        return related_products[:limit]

    def latest_products(self, limit):
        # threshold of 30 days
        post_time_threshold = datetime.now() - timedelta(days=30)
        # select products available in stock
        latest_products = Product.objects.filter\
            (quantity__gte=1, created_at__gte=post_time_threshold)\
            .order_by('-created_at')[:limit]
        return latest_products