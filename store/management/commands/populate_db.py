from django.core.management.base import BaseCommand, CommandError
from store.models import *

class Command(BaseCommand):
    help = "Populate database with basic clothing categories, brands etc"

    def _populate(self):
        brand1 = Brand(name='Nike',
            email="store@nike.com", phone="+123445678",
            desc="Nike Inc", brand_image_url=None
        )
        brand1.save()

        brand2 = Brand(name='Addidas',
            email="store@addidas.com", phone="+123445687",
            desc="Addidas Inc", brand_image_url=None
        )
        brand2.save()

        brand3 = Brand(name='Supreme',
            email="store@supreme.com", phone="+123335678",
            desc="Supreme Inc", brand_image_url=None
        )
        brand3.save()

        brand4 = Brand(name='Afro',
            email="store@wavesofafro.com", phone="+2348045678",
            desc="Waves of Afro", brand_image_url=None
        )
        brand4.save()

        brand5 = Brand(name='Gucci',
            email="store@gucci.com", phone="+1231456781",
            desc="Gucci stores", brand_image_url=None
        )
        brand5.save()

        product_category1 = ProductCategory(name='Shirts',
            cat_type="top", desc="Shirts, T-Shirts etc",
            cat_image_url=None
        )
        product_category1.save()

        product_category2 = ProductCategory(name='Trousers',
            cat_type="bottom", desc="Trousers",
            cat_image_url=None
        )
        product_category2.save()


        product_category3 = ProductCategory(name='Jeans',
            cat_type="bottom", desc="Jeans",
            cat_image_url=None
        )
        product_category3.save()


        product_category4 = ProductCategory(name='Trainers',
            cat_type="foot", desc="Trainers",
            cat_image_url=None
        )
        product_category4.save()


        product_category5 = ProductCategory(name='Lapels',
            cat_type="accessory", desc="Lapels",
            cat_image_url=None
        )
        product_category5.save()

        size_format = models.CharField(max_length=15, verbose_name='size format e.g UK, US')
        value = models.CharField(max_length=10, verbose_name='size value e.g 43 or XL')

        size1 = Size(category=product_category1, size_format="", value="S")
        size1.save()
        size2 = Size(category=product_category1, size_format="", value="M")
        size2.save()
        size3 = Size(category=product_category1, size_format="", value="L")
        size3.save()
        size4 = Size(category=product_category1, size_format="", value="XL")
        size4.save()

        size5 = Size(category=product_category2, size_format="", value="S")
        size5.save()
        size6 = Size(category=product_category2, size_format="", value="M")
        size6.save()
        size7 = Size(category=product_category2, size_format="", value="L")
        size7.save()
        size8 = Size(category=product_category2, size_format="", value="XL")
        size8.save()

        size9 = Size(category=product_category4, size_format="UK", value="9")
        size9.save()
        size10 = Size(category=product_category4, size_format="UK", value="10")
        size10.save()
        size11 = Size(category=product_category4, size_format="UK", value="11")
        size11.save()
        size12 = Size(category=product_category4, size_format="UK", value="12")
        size12.save()

        product1 = Product(admin=None, brand=brand1, category=product_category1,
            gender="unisex", name='Nice T-Shirt',
            desc="Wear anytime of the day", size=size2,
            colour="black", price_per_unit=2000, quantity=15
        )
        product1.save()

        product2 = Product(admin=None, brand=brand2, category=product_category4,
            gender="unisex", name='The New Addidas Trainers 4',
            desc="very durable for jogging", size=size11,
            colour="white", price_per_unit=13000, quantity=10
        )
        product2.save()


        product3 = Product(admin=None, brand=brand3, category=product_category3, gender="male",
            name='Stressed Jeans', desc="Wear anytime of the day", size=size3,
            colour="blue", price_per_unit=5000, quantity=5
        )
        product3.save()


        product4 = Product(admin=None, brand=None, category=product_category5, gender="unisex",
            name='Lionhead Lapels', desc="Enhance your style", size=None,
            colour="black", price_per_unit=2000, quantity=15
        )
        product4.save()

    def handle(self, *args, **options):
        self._populate()

        self.stdout.write(self.style.SUCCESS("Seeding complete!"))