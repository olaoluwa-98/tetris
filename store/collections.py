import calendar
from datetime import datetime, timedelta
from .models import Brand, Product, Wish, Order, OrderItem, ProductCategory
from django.contrib.auth import get_user_model
from django.db.models import Q


# This class preprocesses and returns different collections
class Collections:
    def popular_brands(self, limit):
        # threshold of 30 days
        post_time_threshold = datetime.now() - timedelta(days=30)
        brands = Brand.objects.all()
        popular_brands = sorted(
            brands,
            key=lambda b: (86400 * b.get_wishes().count() * 86400 * b.get_orders().count() * 86400 * b.get_carts().count())
                + calendar.timegm(b.created_at.utctimetuple()),
            # reverse=True
        )
        return popular_brands[:limit]

    def popular_products(self, limit):
        # threshold of 30 days
        post_time_threshold = datetime.now() - timedelta(days=30)

        # select products available in stock
        products = Product.objects.filter(quantity__gte=1)
        products = products.filter(created_at__gte=post_time_threshold)
        popular_products = sorted(
            products,
            key=lambda p: (86400 * p.get_wishes().count() * 86400 * p.get_orders().count() * 86400 * p.get_carts().count())
                + calendar.timegm(p.created_at.utctimetuple()),
            reverse=True
        )
        return popular_products[:limit]

    def latest_products(self, limit):
        # threshold of 7 days
        post_time_threshold = datetime.now() - timedelta(days=7)

        # select products available in stock
        latest_products = Product.objects.filter(quantity__gte=1, created_at__gte=post_time_threshold).order_by('created_at')
        return latest_products[:limit]

    def categories(self, limit = 5):
        categories = ProductCategory.objects.all()
        return categories[:limit]


    def related_products(self, product, limit=5):
        related_products = Product.objects.filter(
            gender=product.gender
        ).exclude(pk=product.pk)

        # sort by wish and datetime
        # related_products = sorted(
        #     related_products,
        #     key=lambda p: (86400 * p.get_orders().count()) + calendar.timegm(p.created_at.utctimetuple()),
        #     reverse=True
        # )
        return related_products[:limit]