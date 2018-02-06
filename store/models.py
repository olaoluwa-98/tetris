from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from .addresses import STATES
from autoslug import AutoSlugField
from django.urls import reverse
from phonenumber_field.modelfields import PhoneNumberField

# this returns the location of the uploaded profile picture
def get_profile_pic_path(instance, filename):
    return 'profile_pictures/{}-{}'.format(instance.user.username, filename)

class User(AbstractUser):
    email = models.EmailField( verbose_name='email address', unique=True)
    email_token = models.CharField(verbose_name='email token', max_length=16, editable=False, null=True)
    is_verified = models.BooleanField(default=False)
    phone = PhoneNumberField(blank=True, null=True,
        help_text='Please use the following format: <em>+234 XXX XXX XXXX</em>.',
    )
    profile_pic_path = models.ImageField(upload_to=get_profile_pic_path, max_length=255)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    # Override models save method:
    def save(self, *args, **kwargs):
        if not self.pk:
            # generate email_token for the user
            # email_token must be unique
            self.email_token = '{}{}'.format(self.email[:2], get_random_string(length=14))
            while User.objects.filter(email_token=self.email_token).exists():
                self.email_token = '{}{}'.format(self.email[:2], get_random_string(length=14))
        super(User, self).save(*args, **kwargs)

    def __str__(self):
        return '{}'.format(self.email)


class Brand(models.Model):
    name = models.CharField(max_length=40, unique=True, verbose_name='name of the brand' )
    email = models.EmailField( max_length=50, verbose_name='email address of the brand')
    phone = PhoneNumberField(blank=True, null=True,
        help_text='Please use the following format: <em>+234 XXX XXX XXXX</em>.',
    )
    desc = models.CharField(max_length=255, verbose_name='description of brand', blank=True, null=True)
    brand_image_url = models.ImageField(upload_to='img/brands/', max_length=255, blank=True, null=True)
    slug = AutoSlugField(populate_from='name',
        unique=True,
        sep='',
        )
    created_at = models.DateTimeField(auto_now_add=True, editable=False,
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

    def random_product_images(self):
        from django.db.models import Count
        products = list(self.products.all()[:3])
        images = []
        if len(products) > 0:
            for product in products:
                images.append(ProductImage.objects.filter(product=product).first())
            if len(images) > 0:
                return images
        return None

    def __str__(self):
        return '{}'.format(self.name)

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
    created_at = models.DateTimeField(auto_now_add=True, editable=False,
        verbose_name='date added'
    )
    updated_at = models.DateTimeField( auto_now=True, verbose_name='date shipping address details were updated last' )

    def __str__(self):
        return '{}, {}. ({})'.format(self.city, self.state, self.user.username)

    class Meta:
        verbose_name_plural = 'Shipping Addresses'
        get_latest_by = 'created_at'
        ordering  = ['user_id',]

class ProductCategory(models.Model):
    name = models.CharField(max_length=30, unique=True, verbose_name='name of category')
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
    created_at = models.DateTimeField(auto_now_add=True, editable=False,
        verbose_name='date product category was added to db'
    )
    updated_at = models.DateTimeField( auto_now=True, verbose_name='date product category details were updated last')

    def get_absolute_url(self):
        return reverse('store:category', kwargs={'slug': self.slug})

    def random_product_images(self):
        from django.db.models import Count
        products = list(self.products.all()[:3])
        images = []
        if len(products) > 0:
            for product in products:
                images.append(ProductImage.objects.filter(product=product).first())
            if len(images) > 0:
                return images
        return None

    def __str__(self):
        return '{} ({})'.format(self.name, self.cat_type)

    class Meta:
        get_latest_by = 'created_at'
        verbose_name_plural = 'Product Categories'
        ordering  = ['name',]


class Product(models.Model):
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
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
    price_per_unit = models.DecimalField(decimal_places=2, max_digits=17, verbose_name='price (₦)')
    quantity = models.PositiveIntegerField(verbose_name='quantity left')
    num_deliveries = models.PositiveIntegerField(verbose_name='deliveries', default=0)
    orders_count = models.PositiveIntegerField(verbose_name='orders', default=0)
    slug = AutoSlugField(populate_from='name',
        unique=True,
        sep='',
    )
    created_at = models.DateTimeField(auto_now_add=True, editable=False,
        verbose_name='date added'
    )
    updated_at = models.DateTimeField( auto_now=True, verbose_name='date product details were updated last' )

    def get_absolute_url(self):
        return reverse('store:product', kwargs={'slug': self.slug})

    def __str__(self):
        return '{}'.format(self.name)

    class Meta:
        get_latest_by = 'created_at'
        ordering  = ['-created_at', 'admin_id', 'name']


class Wish(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wishes',
        verbose_name ='Owner'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='wishes',
        verbose_name ='Product'
    )
    created_at = models.DateTimeField(auto_now_add=True, editable=False,
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
        return '{} -> {}'.format(self.user.username, self.product.name)

    class Meta:
        get_latest_by = 'created_at'
        verbose_name_plural = 'wishes'
        ordering  = ['-created_at', 'user_id']


class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name ='Owner',
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
    created_at = models.DateTimeField(auto_now_add=True, editable=False,
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
        return 'x{} {} -> {}'.format(self.quantity, self.user, self.product.name)

    class Meta:
        get_latest_by = 'created_at'
        ordering  = ['-created_at', 'user_id']


class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='orders',
        verbose_name ='Customer'
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
    ref = models.CharField(verbose_name='reference',max_length=100,null=True,blank=True,
        help_text='this field is generated automatically'
    )
    reason_cancelled = models.CharField(verbose_name='if order is cancelled, why?',max_length=100,blank=True,null=True)
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
    deliver_date = models.DateTimeField(null=True, blank=True,
        verbose_name='delivered (tetris)'
    )
    confirm_delivery_date = models.DateTimeField(null=True, blank=True,
        verbose_name='confirmed delivered (customer)'
    )
    created_at = models.DateTimeField(auto_now_add=True, editable=False,
        verbose_name='date ordered'
    )
    updated_at = models.DateTimeField( auto_now=True, verbose_name='date order details were updated last' )

    def subtotal(self):
        from django.db.models import Sum, F
        total = self.order_items.aggregate( subtotal=Sum(F('price_per_unit') * F('quantity'), output_field=models.DecimalField()))
        if total['subtotal']:
            return total['subtotal']
        return 0

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
        return '{} ordered {} [{}]'.format(self.user.username, self.ref, self.status)

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
    created_at = models.DateTimeField(auto_now_add=True, editable=False,
        verbose_name='date ordered'
    )
    updated_at = models.DateTimeField( auto_now=True, verbose_name='date order details were updated last' )

    def __str__(self):
        return 'x{} {} [{}]'.format(self.quantity, self.product.name, self.order.ref)

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
    created_at = models.DateTimeField(auto_now_add=True, editable=False,
        verbose_name='date image was added to db'
    )
    updated_at = models.DateTimeField( auto_now=True, verbose_name='date image was updated last' )

    def __str__(self):
        return '{}\'s image'.format(self.product.name)

    class Meta:
        verbose_name_plural = 'Product Images'
        get_latest_by = 'created_at'
        ordering  = ['product_id',]

# Not sure to add this.
# class Size(models.Model):
#     size_format = models.CharField(max_length=15, verbose_name='size format e.g UK, US')
#     value = models.IntegerField(verbose_name='size value')
#     post_fix = models.CharField(max_length=10, verbose_name='post fix of size value e.g 27cm')
#     created_at = models.DateTimeField(auto_now_add=True, editable=False,
#         verbose_name='date size was added to db'
#     )
#     updated_at = models.DateTimeField( auto_now=True, verbose_name='date size details were updated last' )

#     class Meta:
#         get_latest_by = 'created_at'
#         ordering  = ['size_format']