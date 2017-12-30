from django.conf import settings
from django.urls import reverse
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.auth import get_user_model
from datetime import datetime
from django.utils.crypto import get_random_string
from .addresses import STATES

# this is for when a user gets deleted from the db
def get_sentinel_user():
    return get_user_model().objects.get_or_create(username='deleted-'+get_random_string(length=10), is_verified=0, is_active=0)[0]

# this returns the location of the uploaded profile picture
def get_profile_pic_path(instance, filename):
    return 'profile_pictures/{0}-{1}'.format(instance.user.username, filename)

class User(AbstractUser):
    is_verified = models.BooleanField(default=False)
    phone = models.CharField(
        max_length=15, verbose_name='phone number of the user',
        help_text='Please use the following format: <em>+234 XXX XXX XXXX</em>.',
        # validators=[]
    )
    profile_pic_path = models.ImageField(upload_to=get_profile_pic_path, max_length=255)
    # USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['email', 'is_verified', 'phone']

    def get_wish(self):
        return Wish.objects.filter(user=self).order_by('-created_at')
    def get_cart(self):
        return Cart.objects.filter(user=self).order_by('-created_at')

    def __str__(self):
        return '{0} {1} (@{2}) admin({3})'.format(self.first_name, self.last_name, self.username, self.is_superuser)


class Brand(models.Model):
    name = models.CharField( max_length=40, unique=True, verbose_name='name of the brand' )
    email = models.EmailField( max_length=50, verbose_name='email address of the brand')
    phone = models.CharField(
        max_length=15, verbose_name='phone number of the brand',
    	help_text='Please use the following format: <em>+234 XXX XXX XXXX</em>.',
    	# validators=[]
    )
    created_at = models.DateTimeField( default=datetime.now(), editable=False,
    	verbose_name='date brand was added to db'
    )
    updated_at = models.DateTimeField( auto_now=True, verbose_name='date brand details were updated last' )

    def __str__(self):
        return '{0} ({1})'.format(self.name, self.email)

    class Meta:
        get_latest_by = 'created_at'
        # verbose_name_plural = 'stories'
        # order_with_respect_to = 'question'

        # not sure if I should add these
        # ordering  = ['-created_at', 'name']
        # permissions = (('can_have_items', 'Can have items'),)

class ShippingAddress(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET(get_sentinel_user),
        related_name='shipping_addresses_owner',
        verbose_name ='User from the user table'
    )
    zip_code = models.CharField( max_length=10, verbose_name='zip code' )
    address = models.CharField( max_length=60, verbose_name='address' )
    city = models.CharField( max_length=30, verbose_name='city' )
    state = models.CharField( max_length=15, verbose_name='state', choices=STATES )
    country = models.CharField( max_length=30, default='Nigeria', verbose_name='country' )
    created_at = models.DateTimeField( default=datetime.now(), editable=False,
        verbose_name='date shipping address was added to db'
    )
    updated_at = models.DateTimeField( auto_now=True, verbose_name='date shipping address details were updated last' )

    def __str__(self):
        return '{0}, {1}, {2}. ({3})'.format(self.address, self.city, self.state, self.user.username)

class ProductCategory(models.Model):
    name = models.CharField(max_length=30, verbose_name='name of category')
    CAT_TYPES = (
        ('top', 'Top'),
        ('bottom', 'Bottom'),
        ('other', 'Other')
    )
    cat_type = models.CharField(max_length=10, choices=CAT_TYPES, verbose_name='type of category')
    created_at = models.DateTimeField( default=datetime.now(), editable=False,
        verbose_name='date product category was added to db'
    )
    updated_at = models.DateTimeField( auto_now=True, verbose_name='date product category details were updated last' )

    def __str__(self):
        return '{0} ({1})'.format(self.name, self.cat_type)

    class Meta:
        get_latest_by = 'created_at'
        verbose_name_plural = 'Product Categories'
        ordering  = ['name',]


class Product(models.Model):
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET(get_sentinel_user),
        related_name='product_adder',
        verbose_name ='Admin from the user table'
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name='product_brand',
        verbose_name ='Brand of the Product'
    )
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.CASCADE,
        related_name='product_category',
        verbose_name ='Category of the Product'
    )
    GENDER = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('unisex', 'Unisex')
    )
    name = models.CharField(max_length=50, verbose_name='name of product')
    gender = models.CharField(max_length=15, choices=GENDER, verbose_name='gender of product')
    size = models.CharField(max_length=15, verbose_name='size of product')
    colour = models.CharField(max_length=15, verbose_name='colour of product')
    price = models.DecimalField(decimal_places=2, max_digits=17)
    quantity = models.IntegerField(verbose_name='current quantity in store')
    product_url = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField( default=datetime.now(), editable=False,
        verbose_name='date product was added to db'
    )
    updated_at = models.DateTimeField( auto_now=True, verbose_name='date product details were updated last' )

    # Override models save method:
    def save(self, *args, **kwargs):
        if not self.id:
            # generate product url when post is created
            # product url must be unique
            self.product_url = '/product/' + get_random_string(length=16) + '/'
            while Product.objects.filter(product_url=self.product_url).exists():
                self.product_url = '/product/' + get_random_string(length=16) + '/'
        super(Product, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return ''.format(self.product_url)

    def __str__(self):
        return '{0} {1} [{2}, {3}] ({4})'.format(self.brand.name, self.name, self.gender, self.category.name, self.admin.username)

    class Meta:
        get_latest_by = 'created_at'
        ordering  = ['-created_at', 'admin_id', 'name']


class Wish(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        # on_delete=models.SET(get_sentinel_user),
        on_delete=models.CASCADE,
        related_name='wish_owner',
        verbose_name ='User from the user table'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='wish_product',
        verbose_name ='Product'
    )
    created_at = models.DateTimeField( default=datetime.now(), editable=False,
        verbose_name='date wish was added to db'
    )
    updated_at = models.DateTimeField( auto_now=True, verbose_name='date wish details were updated last' )

    # Override models save method:
    def save(self, *args, **kwargs):
        # check if wish item already exists, if it does ignore
        if Wish.objects.filter(user_id=self.user_id, product_id=self.product_id).exists():
            pass
        else:
            super(Wish, self).save(*args, **kwargs)

    def __str__(self):
        return '{0} -> {1} (added {2})'.format(self.user.username, self.product.name, self.created_at)

    class Meta:
        get_latest_by = 'created_at'
        verbose_name_plural = 'wishes'
        ordering  = ['-created_at', 'user_id']


class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET(get_sentinel_user),
        related_name='cart_owner',
        verbose_name ='User from the user table'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_product',
        verbose_name ='product in the cart'
    )
    quantity = models.IntegerField(verbose_name='quantity of the item added')
    created_at = models.DateTimeField( default=datetime.now(), editable=False,
        verbose_name='date cart item was added to db'
    )
    updated_at = models.DateTimeField( auto_now=True, verbose_name='date cart item details were updated last' )

    # Override models save method:
    def save(self, *args, **kwargs):
        # check if cart item already exists, add more quantity to it
        cart = Cart.objects.filter(user_id=self.user_id, product_id=self.product_id)
        if len(cart) == 1:
            cart[0].quantity += self.quantity
            super(Cart, cart[0]).save(*args, **kwargs)
        else:
            super(Cart, self).save(*args, **kwargs)

    def __str__(self):
        return 'x{0} {1} -> {2} (added {3})'.format(self.quantity, self.user.username, self.product.name, self.created_at)

    class Meta:
        get_latest_by = 'created_at'
        ordering  = ['-created_at', 'user_id']


# Not sure to add this.
# class Size(models.Model):
#     size_format = models.CharField(max_length=15, verbose_name='size format e.g UK, US')
#     value = models.IntegerField(verbose_name='size value')
#     post_fix = models.CharField(max_length=10, verbose_name='post fix of size value e.g 27cm')
#     created_at = models.DateTimeField( default=datetime.now(), editable=False,
#         verbose_name='date size was added to db'
#     )
#     updated_at = models.DateTimeField( auto_now=True, verbose_name='date size details were updated last' )

#     class Meta:
#         get_latest_by = 'created_at'
#         ordering  = ['size_format']