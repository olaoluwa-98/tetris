from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.auth import get_user_model
from datetime import datetime
from django.utils.crypto import get_random_string
from .addresses import STATES
from autoslug import AutoSlugField
from django.urls import reverse

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
        blank=True, null=True
        # validators=[]
    )
    profile_pic_path = models.ImageField(upload_to=get_profile_pic_path, max_length=255)
    # USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['email', 'is_verified', 'phone']

    def full_name(self):
        return '{0} {1}'.format(self.first_name, self.last_name)

    def __str__(self):
        return '{0} {1} (@{2})'.format(self.first_name, self.last_name, self.username)


class Brand(models.Model):
    name = models.CharField( max_length=40, unique=True, verbose_name='name of the brand' )
    email = models.EmailField( max_length=50, verbose_name='email address of the brand')
    phone = models.CharField(
        max_length=15, verbose_name='phone number of the brand',
    	help_text='Please use the following format: <em>+234 XXX XXX XXXX</em>.',
    	# validators=[]
    )
    desc = models.CharField(max_length=255, verbose_name='description of brand', blank=True, null=True)
    brand_image_url = models.ImageField(upload_to='img/brands/', max_length=255, blank=True, null=True)
    slug = AutoSlugField(populate_from='name',
        unique=True,
        sep='',
        )
    created_at = models.DateTimeField( default=datetime.now(), editable=False,
        verbose_name='date brand was added to db'
    )

    updated_at = models.DateTimeField( auto_now=True, verbose_name='date brand details were updated last' )

    def get_absolute_url(self):
        return reverse('store:brand', kwargs={'slug': self.slug})

    def get_carts(self):
        return Cart.objects.filter(product__brand=self).order_by('-created_at')

    def get_wishes(self):
        return Wish.objects.filter(product__brand=self).order_by('-created_at')

    def get_orders(self):
        return OrderItem.objects.filter(product__brand=self).order_by('-created_at')

    def __str__(self):
        return '{0} ({1})'.format(self.name, self.email)

    class Meta:
        get_latest_by = 'created_at'

class ShippingAddress(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='shipping_addresses',
        verbose_name ='Customer'
    )
    is_default = models.BooleanField(default=False)
    zip_code = models.CharField( max_length=10, verbose_name='zip code' )
    address = models.CharField( max_length=60, verbose_name='address' )
    city = models.CharField( max_length=30, verbose_name='city' )
    state = models.CharField( max_length=15, verbose_name='state', choices=STATES )
    country = models.CharField( max_length=30, default='Nigeria', verbose_name='country' )
    created_at = models.DateTimeField( default=datetime.now(), editable=False,
        verbose_name='date added'
    )
    updated_at = models.DateTimeField( auto_now=True, verbose_name='date shipping address details were updated last' )

    def __str__(self):
        return '{0}, {1}. ({2})'.format(self.city, self.state, self.user.username)

    class Meta:
        verbose_name_plural = 'Shipping Addresses'
        get_latest_by = 'created_at'
        ordering  = ['user_id',]

class ProductCategory(models.Model):
    name = models.CharField(max_length=30, verbose_name='name of category')
    CAT_TYPES = (
        ('top', 'Top'),
        ('bottom', 'Bottom'),
        ('accessory', 'Accessory'),
        ('foot', 'Footwear'),
        ('other', 'Other')
    )
    cat_type = models.CharField(max_length=10, choices=CAT_TYPES, verbose_name='type of category')
    desc = models.CharField(max_length=255, verbose_name='description of product category', blank=True, null=True)
    cat_image_url = models.ImageField(upload_to='img/product_categories/', max_length=255, blank=True, null=True)
    slug = AutoSlugField(populate_from='name',
        unique=True,
        sep='',
    )
    created_at = models.DateTimeField( default=datetime.now(), editable=False,
        verbose_name='date product category was added to db'
    )
    updated_at = models.DateTimeField( auto_now=True, verbose_name='date product category details were updated last')

    def get_absolute_url(self):
        return reverse('store:category', kwargs={'slug': self.slug})

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
        related_name='products',
        verbose_name ='Staff',
        blank=True,
        null=True
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='products',
        verbose_name ='Brand'
    )
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='products',
        verbose_name ='Category'
    )
    GENDER = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('unisex', 'Unisex')
    )
    COLOURS = (
        ('blue', 'Blue'),
        ('red', 'Red'),
        ('white', 'White'),
        ('black', 'Black'),
        ('green', 'Green'),
        ('purple', 'Purple'),
        ('yellow', 'Yellow'),
        ('gray', 'Gray'),
        ('khaki', 'Khaki'),
        ('brown', 'Brown'),
        ('orange', 'Orange'),
        ('navy blue', 'Navy Blue'),
        ('transparent', 'Transparent'),
        ('gold', 'Gold'),
        ('silver', 'Silver'),
    )
    SIZES = (
        ('EUR-39', 'EUR 39'),
    )
    name = models.CharField(max_length=50, verbose_name='name')
    desc = models.CharField(max_length=255, verbose_name='description', blank=True, null=True)
    gender = models.CharField(max_length=15, choices=GENDER, verbose_name='gender')
    size = models.CharField(max_length=15, verbose_name='size')
    colour = models.CharField(max_length=15, verbose_name='colour', choices=COLOURS)
    price_per_unit = models.DecimalField(decimal_places=2, max_digits=17, verbose_name='price in ₦')
    quantity = models.PositiveIntegerField(verbose_name='quantity left')
    num_deliveries = models.PositiveIntegerField(verbose_name='number of deliveries', default=0)
    orders_count = models.PositiveIntegerField(verbose_name='number of order', default=0)
    slug = AutoSlugField(populate_from='name',
        unique=True,
        sep='',
    )
    created_at = models.DateTimeField( default=datetime.now(), editable=False,
        verbose_name='date added'
    )
    updated_at = models.DateTimeField( auto_now=True, verbose_name='date product details were updated last' )

    def get_absolute_url(self):
        return reverse('store:product', kwargs={'slug': self.slug})

    def __str__(self):
        return '{0}'.format(self.name)

    class Meta:
        get_latest_by = 'created_at'
        ordering  = ['-created_at', 'admin_id', 'name']


class Wish(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wishes',
        verbose_name ='User from the user table'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='wishes',
        verbose_name ='Product'
    )
    created_at = models.DateTimeField( default=datetime.now(), editable=False,
        verbose_name='date wish was added to db'
    )
    updated_at = models.DateTimeField( auto_now=True, verbose_name='date wish details were updated last' )

    # Override models save method:
    def save(self, *args, **kwargs):
        # check if wish product already exists, if it does ignore
        if Wish.objects.filter(user_id=self.user_id, product_id=self.product_id).exists():
            pass
        else:
            super(Wish, self).save(*args, **kwargs)

    def __str__(self):
        return '{0} -> {1}'.format(self.user.username, self.product.name)

    class Meta:
        get_latest_by = 'created_at'
        verbose_name_plural = 'wishes'
        ordering  = ['-created_at', 'user_id']


class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name ='User from the user table',
        blank=True,
        null=True
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='cart',
        verbose_name ='product in the cart'
    )
    quantity = models.PositiveIntegerField(verbose_name='quantity of the product added')
    created_at = models.DateTimeField( default=datetime.now(), editable=False,
        verbose_name='date cart product was added to db'
    )
    updated_at = models.DateTimeField( auto_now=True, verbose_name='date cart product details were updated last' )

    # Override models save method:
    def save(self, *args, **kwargs):
        # check if cart product already exists, add more quantity to it
        if not self.pk:
            cart = Cart.objects.filter(user=self.user, product_id=self.product_id)
            if cart.exists():
                cart_item = cart.first()
                cart_item.quantity += int(self.quantity)
                super(Cart, cart_item).save(*args, **kwargs)
            else:
                super(Cart, self).save(*args, **kwargs)
        else:
            super(Cart, self).save(*args, **kwargs)

    def __str__(self):
        return 'x{0} {1} -> {2}'.format(self.quantity, self.user, self.product.name)

    class Meta:
        get_latest_by = 'created_at'
        ordering  = ['-created_at', 'user_id']


class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='orders',
        verbose_name ='customer'
    )
    shipping_address = models.ForeignKey(
        ShippingAddress,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='orders',
        verbose_name ='shipping address',
    )
    ORDER_STATUS = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled')
    )
    ref = models.CharField(verbose_name='reference', max_length=100, null=True,
        help_text='type anything in this field. it\'ll be generated automatically'
    )
    reason_cancelled = models.CharField(verbose_name='if cancelled, why?', max_length=100, null=True)
    canceller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='cancellers',
        verbose_name ='the canceller',
    )
    status = models.CharField(choices=ORDER_STATUS, default='pending', max_length=100,
        verbose_name='status'
    )
    deliver_date = models.DateTimeField(null=True, verbose_name='date order was delivered'
    )
    created_at = models.DateTimeField( default=datetime.now(), editable=False,
        verbose_name='date ordered'
    )
    updated_at = models.DateTimeField( auto_now=True, verbose_name='date order details were updated last' )

    def get_absolute_url(self):
        return reverse('store:order', kwargs={'ref': self.ref})

    # Override models save method:
    def save(self, *args, **kwargs):
        if not self.pk:
            # generate reference for the order
            # order reference must be unique
            self.ref = get_random_string(length=16)
            while Order.objects.filter(ref=self.ref).exists():
                self.ref = get_random_string(length=16)
        super(Order, self).save(*args, **kwargs)

    def __str__(self):
        return '{0} ordered {1} [{2}]'.format(self.user.username, self.ref, self.status)

    class Meta:
        get_latest_by = 'created_at'
        ordering  = ['-created_at', 'user_id']


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='order_items',
        verbose_name ='order'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='order_items',
        verbose_name ='product ordered'
    )
    quantity = models.PositiveIntegerField(verbose_name='quantity ordered')
    price_per_unit = models.DecimalField(decimal_places=2, max_digits=17)
    created_at = models.DateTimeField( default=datetime.now(), editable=False,
        verbose_name='date ordered'
    )
    updated_at = models.DateTimeField( auto_now=True, verbose_name='date order details were updated last' )

    def __str__(self):
        return 'x{0} {1} [{2}]'.format(self.quantity, self.product.name, self.order.ref)

    class Meta:
        verbose_name_plural = 'Order Items'
        get_latest_by = 'created_at'
        ordering  = ['order',]


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='product_images',
        verbose_name ='product image belongs to'
    )
    product_image_url = models.ImageField(upload_to='img/products/', max_length=255, blank=True)
    created_at = models.DateTimeField( default=datetime.now(), editable=False,
        verbose_name='date image was added to db'
    )
    updated_at = models.DateTimeField( auto_now=True, verbose_name='date image was updated last' )

    def __str__(self):
        return '{0}\'s image'.format(self.product.name)

    class Meta:
        verbose_name_plural = 'Product Images'
        get_latest_by = 'created_at'
        ordering  = ['product_id',]

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