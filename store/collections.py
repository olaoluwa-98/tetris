import calendar
from datetime import datetime, timedelta
from .models import Brand, Product, Wish, Order, OrderItem
from django.contrib.auth import get_user_model
from django.db.models import Q


# This class preprocesses and returns different collections
class Collections:
    def popular_brands(self, limit):
        # threshold of 30 days
        post_time_threshold = datetime.now() - timedelta(days=30)
        return Brand.objects.all()
        # popular_brands = sorted(
        #     bran,
        #     key=lambda p: (86400 * p.get_wishes().count() * p.get_orders().count()) + calendar.timegm(p.created_at.utctimetuple()),
        #     reverse=True
        # )

    def popular_products(self, limit):
        # threshold of 30 days
        post_time_threshold = datetime.now() - timedelta(days=30)

        # select products available in stock
        products = Product.objects.filter(quantity__gte=1)
        products = products.filter(created_at__gte=post_time_threshold)
        popular_products = sorted(
            products,
            key=lambda p: (86400 * p.get_wishes().count() * p.get_orders().count()) + calendar.timegm(p.created_at.utctimetuple()),
            reverse=True
        )
        return popular_products[:limit]

    def related_products(self, product, limit=5):
        # uses popular posts in the krak that post is in
        related_products = Product.objects.filter(krak=post.krak).exclude(id=product.id)
        # sort by wish and datetime
        # preference goes to recent posts with more wish
        related_products = sorted(
            related_products,
            key=lambda p: (86400 * p.get_orders().count()) + calendar.timegm(p.created_at.utctimetuple()),
            reverse=True
        )
        return related_products[:limit]