# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-17 09:28
from __future__ import unicode_literals

import autoslug.fields
import datetime
from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import store.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=30, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('is_verified', models.BooleanField(default=False)),
                ('phone', models.CharField(help_text='Please use the following format: <em>+234 XXX XXX XXXX</em>.', max_length=15, verbose_name='phone number of the user')),
                ('profile_pic_path', models.ImageField(max_length=255, upload_to=store.models.get_profile_pic_path)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40, unique=True, verbose_name='name of the brand')),
                ('email', models.EmailField(max_length=50, verbose_name='email address of the brand')),
                ('phone', models.CharField(help_text='Please use the following format: <em>+234 XXX XXX XXXX</em>.', max_length=15, verbose_name='phone number of the brand')),
                ('desc', models.CharField(max_length=255, verbose_name='description of brand')),
                ('brand_image_url', models.ImageField(blank=True, max_length=255, upload_to='img/brands/')),
                ('slug', autoslug.fields.AutoSlugField(editable=False, populate_from='name', sep='', unique=True)),
                ('created_at', models.DateTimeField(default=datetime.datetime(2018, 1, 17, 10, 28, 54, 539545), editable=False, verbose_name='date brand was added to db')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='date brand details were updated last')),
            ],
            options={
                'get_latest_by': 'created_at',
            },
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(verbose_name='quantity of the product added')),
                ('created_at', models.DateTimeField(default=datetime.datetime(2018, 1, 17, 10, 28, 54, 540723), editable=False, verbose_name='date cart product was added to db')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='date cart product details were updated last')),
            ],
            options={
                'ordering': ['-created_at', 'user_id'],
                'get_latest_by': 'created_at',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ref', models.CharField(help_text="type anything in this field. it'll be generated automatically", max_length=100, null=True, verbose_name='reference of the order')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('delivered', 'Delivered'), ('cancelled', 'Cancelled')], default='pending', max_length=100, verbose_name='status of the order e.g pending, processing, cancelled, delivered')),
                ('created_at', models.DateTimeField(default=datetime.datetime(2018, 1, 17, 10, 28, 54, 540723), editable=False, verbose_name='date order was placed')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='date order details were updated last')),
                ('user', models.ForeignKey(on_delete=models.SET(store.models.get_sentinel_user), related_name='orders', to=settings.AUTH_USER_MODEL, verbose_name='User from the user table')),
            ],
            options={
                'ordering': ['-created_at', 'user_id'],
                'get_latest_by': 'created_at',
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(verbose_name='quantity of the product ordered')),
                ('price_per_unit', models.DecimalField(decimal_places=2, max_digits=17, verbose_name='cost of one of the products ordered')),
                ('created_at', models.DateTimeField(default=datetime.datetime(2018, 1, 17, 10, 28, 54, 540723), editable=False, verbose_name='date product was ordered')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='date order details were updated last')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='store.Order', verbose_name='order product belongs to')),
            ],
            options={
                'verbose_name_plural': 'Order Items',
                'ordering': ['order'],
                'get_latest_by': 'created_at',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='name of product')),
                ('desc', models.CharField(max_length=255, verbose_name='description of product')),
                ('gender', models.CharField(choices=[('male', 'Male'), ('female', 'Female'), ('unisex', 'Unisex')], max_length=15, verbose_name='gender of product')),
                ('size', models.CharField(max_length=15, verbose_name='size of product')),
                ('colour', models.CharField(max_length=15, verbose_name='colour of product')),
                ('price_per_unit', models.DecimalField(decimal_places=2, max_digits=17)),
                ('quantity', models.IntegerField(verbose_name='current quantity in store')),
                ('sales_count', models.IntegerField(default=0, verbose_name='number of sales of this product')),
                ('slug', autoslug.fields.AutoSlugField(editable=False, populate_from='name', sep='', unique=True)),
                ('created_at', models.DateTimeField(default=datetime.datetime(2018, 1, 17, 10, 28, 54, 540723), editable=False, verbose_name='date product was added to db')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='date product details were updated last')),
                ('admin', models.ForeignKey(on_delete=models.SET(store.models.get_sentinel_user), related_name='products', to=settings.AUTH_USER_MODEL, verbose_name='Admin from the user table')),
                ('brand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='store.Brand', verbose_name='Brand of the Product')),
            ],
            options={
                'ordering': ['-created_at', 'admin_id', 'name'],
                'get_latest_by': 'created_at',
            },
        ),
        migrations.CreateModel(
            name='ProductCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, verbose_name='name of category')),
                ('cat_type', models.CharField(choices=[('top', 'Top'), ('bottom', 'Bottom'), ('other', 'Other')], max_length=10, verbose_name='type of category')),
                ('desc', models.CharField(max_length=255, verbose_name='description of product category')),
                ('cat_image_url', models.ImageField(blank=True, max_length=255, upload_to='img/product_categories/')),
                ('created_at', models.DateTimeField(default=datetime.datetime(2018, 1, 17, 10, 28, 54, 540723), editable=False, verbose_name='date product category was added to db')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='date product category details were updated last')),
            ],
            options={
                'verbose_name_plural': 'Product Categories',
                'ordering': ['name'],
                'get_latest_by': 'created_at',
            },
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_image_url', models.ImageField(blank=True, max_length=255, upload_to='img/products/')),
                ('created_at', models.DateTimeField(default=datetime.datetime(2018, 1, 17, 10, 28, 54, 540723), editable=False, verbose_name='date image was added to db')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='date image was updated last')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_images', to='store.Product', verbose_name='product image belongs to')),
            ],
            options={
                'verbose_name_plural': 'Product Images',
                'ordering': ['product_id'],
                'get_latest_by': 'created_at',
            },
        ),
        migrations.CreateModel(
            name='ShippingAddress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('zip_code', models.CharField(max_length=10, verbose_name='zip code')),
                ('address', models.CharField(max_length=60, verbose_name='address')),
                ('city', models.CharField(max_length=30, verbose_name='city')),
                ('state', models.CharField(choices=[('Abia', 'Abia'), ('Abuja', 'Abuja'), ('Adamawa', 'Adamawa'), ('Ibom', 'Ibom'), ('Anambra', 'Anambra'), ('Bauchi', 'Bauchi'), ('Bayelsa', 'Bayelsa'), ('Benue', 'Benue'), ('Bornu', 'Bornu'), ('River', 'River'), ('Delta', 'Delta'), ('Ebonyi', 'Ebonyi'), ('Edo', 'Edo'), ('Ekiti', 'Ekiti'), ('Enugu', 'Enugu'), ('Gombe', 'Gombe'), ('Imo', 'Imo'), ('Jigawa', 'Jigawa'), ('Kaduna', 'Kaduna'), ('Kano', 'Kano'), ('Katsina', 'Katsina'), ('Kebbi', 'Kebbi'), ('Kogi', 'Kogi'), ('Kwara', 'Kwara'), ('Lagos', 'Lagos'), ('Nassarawa', 'Nassarawa'), ('Niger', 'Niger'), ('Ogun', 'Ogun'), ('Ondo', 'Ondo'), ('Osun', 'Osun'), ('Oyo', 'Oyo'), ('Plateau', 'Plateau'), ('Rivers', 'Rivers'), ('Sokoto', 'Sokoto'), ('Taraba', 'Taraba'), ('Yobe', 'Yobe'), ('Zamfara', 'Zamfara')], max_length=15, verbose_name='state')),
                ('country', models.CharField(default='Nigeria', max_length=30, verbose_name='country')),
                ('created_at', models.DateTimeField(default=datetime.datetime(2018, 1, 17, 10, 28, 54, 539545), editable=False, verbose_name='date shipping address was added to db')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='date shipping address details were updated last')),
                ('user', models.ForeignKey(on_delete=models.SET(store.models.get_sentinel_user), related_name='shipping_addresses', to=settings.AUTH_USER_MODEL, verbose_name='User from the user table')),
            ],
            options={
                'verbose_name_plural': 'Shipping Addresses',
                'ordering': ['user_id'],
                'get_latest_by': 'created_at',
            },
        ),
        migrations.CreateModel(
            name='Wish',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=datetime.datetime(2018, 1, 17, 10, 28, 54, 540723), editable=False, verbose_name='date wish was added to db')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='date wish details were updated last')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wishes', to='store.Product', verbose_name='Product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wishes', to=settings.AUTH_USER_MODEL, verbose_name='User from the user table')),
            ],
            options={
                'verbose_name_plural': 'wishes',
                'ordering': ['-created_at', 'user_id'],
                'get_latest_by': 'created_at',
            },
        ),
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='store.ProductCategory', verbose_name='Category of the Product'),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='store.Product', verbose_name='product ordered'),
        ),
        migrations.AddField(
            model_name='cart',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart', to='store.Product', verbose_name='product in the cart'),
        ),
        migrations.AddField(
            model_name='cart',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.SET(store.models.get_sentinel_user), related_name='cart', to=settings.AUTH_USER_MODEL, verbose_name='User from the user table'),
        ),
    ]
