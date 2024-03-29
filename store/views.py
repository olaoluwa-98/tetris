from django.shortcuts import render, redirect, reverse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from store.collections import Collections
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime
from store.models import *
from store.forms import *
from store.addresses import STATES
from django.core.mail import send_mail
from django.template import loader
from django.conf import settings
from django.contrib.auth.views import PasswordChangeView
# from django.utils.encoding import force_text
# from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
# from django.utils.encoding import force_bytes

col = Collections()
User = get_user_model()
admins = User.objects.filter(is_staff=True)

def bg_img():
    img = TetrisImage.objects.filter(
        name='background-image').first()
    if img:
        return img.image_url.url
    return '/static/store/img/index-bg.jpg'

def product_img_default():
    img = TetrisImage.objects.filter(
        name='default-product-img').first()
    if img:
        return img.image_url.url
    return '/static/store/img/default-product-img.jpg'

def brand_img_default():
    img = TetrisImage.objects.filter(
        name='default-brand-img').first()
    if img:
        return img.image_url.url
    return ''

def category_img_default():
    img = TetrisImage.objects.filter(
        name='default-category-img').first()
    if img:
        return img.image_url.url
    return ''


def get_cart(request):
    # request.session['cart'] = [{'product_id':1, 'quantity':2}, {'product_id':1, 'quantity':2}]
    # import pdb; pdb.set_trace()
    if request.session.get('cart'):
        product_ids = []
        real_cart = []
        try:
            cart = request.session.get('cart')
            for cart_item in cart:
                real_cart.append(Cart(product_id=cart_item['product_id'],quantity=cart_item['quantity']))
                product_ids.append(cart_item['product_id'])
        except:
            product_ids = []
            request.session['cart'] = []
            real_cart = []
        if request.user.is_authenticated:
            remaining_cart = request.user.cart.exclude(product_id__in=product_ids)
            real_cart += list(remaining_cart)
        return real_cart
    if request.user.is_authenticated:
        return request.user.cart.all()
    return []

# Pagination function.
def paginate(input_list, page, results_per_page=10):
    paginator = Paginator(input_list, results_per_page)
    try:
        output_list = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver 1st page.
        output_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), return last page.
        output_list = paginator.page(paginator.num_pages)
    return output_list

class IndexView(TemplateView):
    template_name = 'store/pages/index.html'

    def get_context_data(self, **kwargs):
        context = {'popular_products':col.popular_products(8)}
        context['popular_brands'] = col.popular_brands(4)
        context['cart_count'] = len(get_cart(self.request))
        context['bg_img'] = bg_img()
        context['product_img_default'] = product_img_default()
        context['brand_img_default'] = brand_img_default()
        context['category_img_default'] = category_img_default()
        if self.request.user.is_authenticated:
            context['wish_list_count'] = self.request.user.wishes.count()
        return context


class CustomerCareView(TemplateView):
    template_name = 'store/pages/customer_care.html'

    def post(self, request, *args, **kwargs):
        context = {}
        context['cart_count'] = len(get_cart(self.request))
        context['bg_img'] = bg_img()
        if self.request.user.is_authenticated:
            context['wish_list_count'] = self.request.user.wishes.count()
        form = FeedbackForm(request.POST or None)
        if form.is_valid():
            email = form.cleaned_data['email']
            content = form.cleaned_data['feedback']
            feedback = Feedback.objects.create(email=email,content=content)
            # send mail to the admins
            subject = 'Someone just submitted a feedback'
            message = ''
            from_email = settings.DEFAULT_FROM_EMAIL or 'Tetris Retails <noreply@tetrisretails.com>'
            recipient_list = ()
            for admin in admins:
                recipient_list += (admin.email,)
            html_message = loader.render_to_string(
            'emails/customer_feedback.html', {'feedback': feedback, 'request':request},
            )
            send_mail(subject, message, from_email, recipient_list, fail_silently=True, html_message=html_message)
            context['success'] = 'Your feedback has been received'
        else:
            context['form'] = form
        return render(request, 'store/pages/customer_care.html', context)

    def get_context_data(self, **kwargs):
        context = {}
        context['bg_img'] = bg_img()
        context['cart_count'] = len(get_cart(self.request))
        if self.request.user.is_authenticated:
            context['wish_list_count'] = self.request.user.wishes.count()
        return context


class TermsView(TemplateView):
    template_name = 'store/pages/terms.html'

    def get_context_data(self, **kwargs):
        context = {'popular_products':col.popular_products(8)}
        context['popular_brands'] = col.popular_brands(4)
        context['cart_count'] = len(get_cart(self.request))
        if self.request.user.is_authenticated:
            context['wish_list_count'] = self.request.user.wishes.count()
        return context


class AboutView(TemplateView):
    template_name = 'store/pages/about.html'

    def get_context_data(self, **kwargs):
        context = {}
        context['cart_count'] = len(get_cart(self.request))
        if self.request.user.is_authenticated:
            context['wish_list_count'] = self.request.user.wishes.count()
        return context


class CartView(TemplateView):
    model = Cart
    template_name = 'store/pages/cart.html'

    def get_context_data(self, **kwargs):
        context = {}
        page = self.request.GET.get('page')
        cart = get_cart(self.request)
        cart_list = paginate(cart, page, 5)
        context['cart_list'] = cart_list
        context['cart_count'] = len(cart)
        context['bg_img'] = bg_img()
        context['product_img_default'] = product_img_default()
        if self.request.user.is_authenticated:
            context['wish_list_count'] = self.request.user.wishes.count()
        return context


class CheckoutView(LoginRequiredMixin, TemplateView):
    template_name = 'store/pages/checkout.html'
    success_url = '/store/'

    def get_context_data(self, **kwargs):
        context = {}
        context['cart'] = get_cart(self.request)
        context['bg_img'] = bg_img()
        context['cart_count'] = len(get_cart(self.request))
        context['wish_list_count'] = self.request.user.wishes.count()
        context['product_img_default'] = product_img_default()
        return context


class WishListView(LoginRequiredMixin, TemplateView):
    template_name = 'store/pages/wish_list.html'
    success_url = '/store/'

    def get_context_data(self, **kwargs):
        context = {}
        page = self.request.GET.get('page')
        wishes = paginate(self.request.user.wishes.all(), page, 5)
        context['cart_count'] = len(get_cart(self.request))
        context['wish_list'] = wishes
        context['bg_img'] = bg_img()
        context['wish_list_count'] = self.request.user.wishes.count()
        context['product_img_default'] = product_img_default()
        return context


class OrdersView(LoginRequiredMixin, TemplateView):
    template_name = 'store/pages/orders.html'
    success_url = '/store/'

    def get_context_data(self, **kwargs):
        page = self.request.GET.get('page')
        orders = paginate(self.request.user.orders.all(), page, 5)
        context = {'orders': orders}
        context['cart_count'] = len(get_cart(self.request))
        context['bg_img'] = bg_img()
        context['wish_list_count'] = self.request.user.wishes.count()
        return context

class OrderDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'store/pages/order_detail.html'
    success_url = '/store/'
    def get_context_data(self, **kwargs):
        order = Order.objects.filter(user= self.request.user, ref=self.kwargs['ref']).first()
        context = {}
        if order:
            context['order'] = order
            page = self.request.GET.get('page')
            order_items = paginate(order.order_items.all(), page, 5)
            if not order_items.object_list.exists():
                order_items = None
            context['order_items'] = order_items
        context['cart_count'] = len(get_cart(self.request))
        context['bg_img'] = bg_img()
        context['product_img_default'] = product_img_default()
        if self.request.user.is_authenticated:
            context['wish_list_count'] = self.request.user.wishes.count()
        return context

class ProductDetailView(TemplateView):
    template_name = 'store/pages/product_detail.html'
    def get_context_data(self, **kwargs):
        product = Product.objects.get(slug=self.kwargs['slug'])
        context = { 'product': product}
        context['related_products'] = col.related_products(product, 4)
        context['cart_count'] = len(get_cart(self.request))
        context['bg_img'] = bg_img()
        context['product_img_default'] = product_img_default()
        if self.request.user.is_authenticated:
            context['wish_list_count'] = self.request.user.wishes.count()
        return context


class ProductsView(TemplateView):
    template_name = 'store/pages/products.html'

    def get_context_data(self, **kwargs):
        product_list = Product.objects.all().order_by('-created_at')
        page = self.request.GET.get('page')
        products = paginate(product_list, page, 8)
        context = {'products':products}
        context['cart_count'] = len(get_cart(self.request))
        context['product_img_default'] = product_img_default()
        if self.request.user.is_authenticated:
            context['wish_list_count'] = self.request.user.wishes.count()
        return context


class BrandDetailView(TemplateView):
    template_name = 'store/pages/brand_detail.html'
    def get_context_data(self, **kwargs):
        brand = Brand.objects.get(slug=self.kwargs['slug'])
        context = { 'brand': brand }
        # context['popular_brand_products'] = col.popular_brand_products(brand, 8)
        page = self.request.GET.get('page')
        brand_products = paginate(brand.products.all().order_by('-created_at'), page, 12)
        context['brand_products'] = brand_products
        context['cart_count'] = len(get_cart(self.request))
        context['product_img_default'] = product_img_default()
        context['brand_img_default'] = brand_img_default()
        if self.request.user.is_authenticated:
            context['wish_list_count'] = self.request.user.wishes.count()
        return context


class StoreView(TemplateView):
    template_name = 'store/pages/store.html'
    success_url = '/store/'

    def get_context_data(self, **kwargs):
        context = {}
        context['popular_brands'] = col.popular_brands(4)
        context['latest_products'] = col.latest_products(8)
        context['categories'] = ProductCategory.objects.order_by('-created_at')[:4]
        context['cart_count'] = len(get_cart(self.request))
        context['product_img_default'] = product_img_default()
        context['brand_img_default'] = brand_img_default()
        context['category_img_default'] = category_img_default()
        if self.request.user.is_authenticated:
            context['wish_list_count'] = self.request.user.wishes.count()
        return context


class MenStoreView(TemplateView):
    template_name = 'store/pages/men.html'

    def get_context_data(self, **kwargs):
        context = {}
        product_list = Product.objects.filter(gender__in=['male', 'unisex'])
        page = self.request.GET.get('page')
        products = paginate(product_list, page, 8)
        context['cart_count'] = len(get_cart(self.request))
        context['products'] = products
        context['product_img_default'] = product_img_default()
        if self.request.user.is_authenticated:
            context['wish_list_count'] = self.request.user.wishes.count()
        return context


class WomenStoreView(TemplateView):
    template_name = 'store/pages/women.html'

    def get_context_data(self, **kwargs):
        context = {}
        product_list = Product.objects.filter(gender__in=['female', 'unisex'])
        page = self.request.GET.get('page')
        products = paginate(product_list, page, 8)
        context['cart_count'] = len(get_cart(self.request))
        context['products'] = products
        context['product_img_default'] = product_img_default()
        if self.request.user.is_authenticated:
            context['wish_list_count'] = self.request.user.wishes.count()
        return context


class SearchView(TemplateView):
    template_name = 'store/pages/search.html'

    def get_context_data(self, **kwargs):
        page = self.request.GET.get('page')
        context = {}
        if self.request.GET.get('q'):
            q = self.request.GET.get('q')
            product_list = col.search_products(q)
            products = paginate(product_list, page, 12)
            context['products'] = products
            context['q'] = self.request.GET.get('q')
        context['cart_count'] = len(get_cart(self.request))
        context['product_img_default'] = product_img_default()
        if self.request.user.is_authenticated:
            context['wish_list_count'] = self.request.user.wishes.count()
        return context


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'store/pages/profile.html'
    success_url = '/store/'

    def post(self, request, *args, **kwargs):
        form = ProfileForm(request.POST or None, request.user)
        context = {'form': form}
        context['wish_list_count'] = self.request.user.wishes.count()
        context['cart_count'] = len(get_cart(self.request))
        context['bg_img'] = bg_img()
        if form.is_valid():
            user = request.user
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.username = form.cleaned_data['username']
            if user.email != form.cleaned_data['email']:
                user.email = form.cleaned_data['email']
                user.is_verified = False
            user.phone = form.cleaned_data['phone']
            user.save()
            context['success'] = 'Your profile has been updated'
            return render(request, 'store/pages/profile.html', context)
        return render(request, 'store/pages/profile.html', context)

    def get_context_data(self, **kwargs):
        context = {}
        context['cart_count'] = len(get_cart(self.request))
        context['bg_img'] = bg_img()
        context['wish_list_count'] = self.request.user.wishes.count()
        return context


class CategoryView(TemplateView):
    template_name = 'store/pages/category.html'

    def get_context_data(self, **kwargs):
        category = ProductCategory.objects.filter(slug=self.kwargs['slug']).first()
        page = self.request.GET.get('page')
        cat_products = None
        if category and category.products.exists():
            cat_products = paginate(category.products.all().order_by('-created_at'), page, 12)
        context = { 'category': category }
        context['cat_products'] =  cat_products
        context['cart_count'] = len(get_cart(self.request))
        context['product_img_default'] = product_img_default()
        context['category_img_default'] = category_img_default()
        if self.request.user.is_authenticated:
            context['wish_list_count'] = self.request.user.wishes.count()
        return context


class ShippingAddressesView(LoginRequiredMixin, TemplateView):
    template_name = 'store/pages/shipping_address_list.html'
    success_url = '/store/'

    def get_context_data(self, **kwargs):
        shipping_addresses = ShippingAddress.objects.filter(user = self.request.user)
        context = {'shipping_addresses':shipping_addresses}
        context['cart_count'] = len(get_cart(self.request))
        context['wish_list_count'] = self.request.user.wishes.count()
        context['bg_img'] = bg_img()
        return context


class NewShippingAddressView(LoginRequiredMixin, TemplateView):
    template_name = 'store/pages/new_shipping_address.html'
    success_url = '/store/'

    def post(self, request, *args, **kwargs):
        form = ShippingAddressForm(request.POST or None)
        context = {}
        context['cart_count'] = len(get_cart(self.request))
        context['wish_list_count'] = self.request.user.wishes.count()
        context['states'] = STATES
        if form.is_valid():
            shipping_address = ShippingAddress()
            shipping_address.user = request.user
            shipping = ShippingAddress.objects.filter(user=request.user, is_default=True)
            if shipping.exists() and request.POST.get('is_default'):
                shipping.update(is_default=False)
                shipping_address.is_default = True
            elif not shipping.exists():
                shipping_address.is_default = True
            shipping_address.zip_code = form.cleaned_data['zip_code']
            shipping_address.address = form.cleaned_data['address']
            shipping_address.city = form.cleaned_data['city']
            shipping_address.state = form.cleaned_data['state']
            shipping_address.save()
            context['success'] = 'Your shipping address has been uploaded'
            return render(request, 'store/pages/new_shipping_address.html', context)
        context['form'] = form
        context['bg_img'] = bg_img()
        return render(request, 'store/pages/new_shipping_address.html', context)

    def get_context_data(self, **kwargs):
        context = {}
        form = ShippingAddressForm(None)
        context['form'] = form
        context['states'] = STATES
        context['cart_count'] = len(get_cart(self.request))
        context['wish_list_count'] = self.request.user.wishes.count()
        context['bg_img'] = bg_img()
        return context


class ShippingAddressDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'store/pages/shipping_address_detail.html'
    success_url = '/store/'

    def get_context_data(self, **kwargs):
        num = int(self.kwargs['num'])
        shipping_addresses = ShippingAddress.objects.filter(user=self.request.user)
        if shipping_addresses.count() >= num:
            shipping_address = shipping_addresses[num - 1]
        else:
            shipping_address = None
        context = {'shipping_address':shipping_address}
        form = ShippingAddressForm(None)
        context['form'] = form
        context['shipping_address_num'] = num
        context['states'] = STATES
        if self.request.GET.get('msg'):
            context['success'] = self.request.GET.get('msg')
        context['cart_count'] = len(get_cart(self.request))
        context['wish_list_count'] = self.request.user.wishes.count()
        context['bg_img'] = bg_img()
        return context

@login_required(login_url='/login/')
def update_shipping_address(request):
    form = ShippingAddressForm(request.POST or None)
    if form.is_valid():
        shippings = ShippingAddress.objects.filter(user=request.user, is_default=True)
        shipping_address = ShippingAddress.objects.filter(
            user=request.user, pk=request.POST['shipping_id']
        ).first()
        if request.POST.get('is_default') and shippings.exists():
            shippings.update(is_default=False)
            shipping_address.is_default = True
        shipping_address.zip_code = form.cleaned_data['zip_code']
        shipping_address.address = form.cleaned_data['address']
        shipping_address.city = form.cleaned_data['city']
        shipping_address.state = form.cleaned_data['state']
        shipping_address.save()
        msg = 'Your shipping address has been updated'
        return redirect('/shipping-address/{}/?msg={}'.format(request.POST['shipping_address_num'], msg))
    msg = 'some information you provided is incorrect'
    return redirect('/shipping-address/{}/?msg={}'.format(request.POST['shipping_address_num'], msg))


# AUTH
def handle_login(request):
    if request.user.is_authenticated:
        return redirect('/')
    form = LoginForm(request.POST or None)
    if form.is_valid():
        user = authenticate(username=form.cleaned_data['email'], password=form.cleaned_data['password'])
        if user is not None:
            login(request, user)
            if request.session.get('cart'):
                cart = request.session['cart']
                for cart_item in cart:
                    if not Cart.objects.filter(user=user, product_id=cart_item['product_id']).exists():
                        cart_item = Cart(user=user, product_id=cart_item['product_id'],quantity=cart_item['quantity'])
                        cart_item.save()
            return redirect(request.POST['redirect_url'])
    context = {'form': form}
    context['cart_count'] = len(get_cart(request))
    context['bg_img'] = bg_img()
    return render(request, 'registration/login.html', context)


def handle_register(request):
    if request.user.is_authenticated:
        return redirect('/')
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data['username'].lower()
        email = form.cleaned_data['email'].lower()
        user = user = User(username=username, email=email)
        user.set_password(form.cleaned_data['password'])
        user.save()
        # send user account verification email
        subject = 'Verify Your Tetris Account'
        message = ''
        from_email = settings.DEFAULT_FROM_EMAIL or 'Tetris Retails <noreply@tetrisretails.com>'
        recipient_list = (user.email, )
        html_message = loader.render_to_string(
          'emails/account_verification_email.html', {'user': user,'request':request},
        )
        send_mail(subject, message, from_email, recipient_list, fail_silently=True, html_message=html_message)

        user = authenticate(username=user.email, password=form.cleaned_data.get('password'))
        if user is not None:
            login(request, user)
            if request.session.get('cart'):
                cart = request.session['cart']
                for cart_item in cart:
                    cart_item = Cart(user=user, product_id=cart_item['product_id'],quantity=cart_item['quantity'])
                    cart_item.save()
            return redirect(request.POST['redirect_url'])
    context = {'form': form}
    context['cart_count'] = len(get_cart(request))
    context['bg_img'] = bg_img()
    return render(request, 'registration/register.html', context)


@login_required(login_url='/login/')
def handle_logout(request):
    logout(request)
    return redirect('/login')


class PasswordChangeViewMod(PasswordChangeView):
    def get_context_data(self, **kwargs):
        context = super(PasswordChangeView, self).get_context_data(**kwargs)
        context['bg_img'] = bg_img()
        return context


# AJAX CALLS
@csrf_exempt
def add_to_cart(request):
    if request.session.get('cart'):
        cart = request.session['cart']
        cart.append({'product_id':request.POST['product_id'], 'quantity':request.POST['quantity']})
        request.session['cart'] = cart
    else:
        request.session['cart'] = [{'product_id':request.POST['product_id'], 'quantity':request.POST['quantity']}]
    if request.user.is_authenticated:
        cart_item = Cart(user=request.user, product_id=request.POST['product_id'], quantity=request.POST['quantity'])
        cart_item.save()
        response = JsonResponse({'status' : 'success', 'msg': 'added successfully' })
        response.status_code = 200
        return response

    response = JsonResponse({'status' : 'success', 'msg': 'added successfully' })
    response.status_code = 200
    return response

@csrf_exempt
def change_cart_item_qty(request):
    if int(request.POST['new_quantity']) < 1:
        response = JsonResponse({'status' : 'error', 'msg': 'quantity less than 0' })
        response.status_code = 422
        return response
    if request.session.get('cart'):
        product_id = request.POST['product_id']
        cart = request.session.get('cart')
        for cart_item in cart:
            if cart_item['product_id'] == product_id:
                cart_item['quantity'] = request.POST['new_quantity']
                break
        request.session['cart'] = cart
    if request.user.is_authenticated:
        cart_item = Cart.objects.filter(user=request.user, product_id=request.POST['product_id']).first()
        if cart_item:
            cart_item.quantity = request.POST['new_quantity']
            cart_item.save()
            response = JsonResponse({'status' : 'success', 'msg': 'quantity changed successfully' })
            response.status_code = 200
            return response
        else:
            cart_item = Cart(user=request.user, product_id=request.POST['product_id'], quantity=request.POST['new_quantity'])
            cart_item.save()

    response = JsonResponse({'status' : 'success', 'msg': 'quantity changed successfully' })
    response.status_code = 200
    return response

@csrf_exempt
def remove_from_cart(request):
    if request.session.get('cart') and request.POST.get('product_id'):
        product_id = request.POST['product_id']
        cart = request.session.get('cart')
        for cart_item in cart:
            if cart_item['product_id'] == product_id:
                cart.remove(cart_item)
                break
        request.session['cart'] = cart
    if request.user.is_authenticated and request.POST.get('product_id'):
        cart_item = Cart.objects.filter(user=request.user, product_id=request.POST['product_id']).first()
        if cart_item:
            cart_item.delete()
            response = JsonResponse({'status' : 'success', 'msg': 'removed successfully' })
            response.status_code = 200
            return response
    response = JsonResponse({'status' : 'success', 'msg': 'removed successfully' })
    response.status_code = 200
    return response

@csrf_exempt
@login_required(login_url='/login/')
def add_to_wish_list(request):
    wish_item = Wish(user=request.user, product_id=request.POST['product_id'])
    if wish_item:
        wish_item.save()
        response = JsonResponse({'status' : 'success', 'msg': 'added successfully' })
        response.status_code = 200
        return response

    response = JsonResponse({'status' : 'error', 'msg': 'error occured, please try again later.' })
    response.status_code = 422
    return response

@csrf_exempt
@login_required(login_url='/login/')
def remove_from_wish_list(request):
    wish_item = Wish.objects.filter(user=request.user, product_id=request.POST['product_id']).first()
    if wish_item:
        wish_item.delete()
        response = JsonResponse({'status' : 'success', 'msg': 'removed successfully' })
        response.status_code = 200
        return response

    response = JsonResponse({'status' : 'error', 'msg': 'error occured, please try again later.' })
    response.status_code = 422
    return response

@csrf_exempt
def empty_cart(request):
    if request.session.get('cart'):
        request.session['cart'] = []
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user)
        cart.delete()
        response = JsonResponse({'status' : 'success', 'msg': 'cart emptied' })
        response.status_code = 200
        return response
    response = JsonResponse({'status' : 'success', 'msg': 'cart emptied' })
    response.status_code = 200
    return response

@csrf_exempt
@login_required(login_url='/login/')
def empty_wish_list(request):
        wishes = Wish.objects.filter(user=request.user)
        wishes.delete()
        response = JsonResponse({'status' : 'success', 'msg': 'wish list emptied' })
        response.status_code = 200
        return response

@csrf_exempt
@login_required(login_url='/login/')
def make_purchase(request):
    if not request.user.shipping_addresses.filter(is_default=True).exists():
        response = JsonResponse({'status' : 'error', 'msg': 'your default shipping address is not set', 'shipping': True })
        response.status_code = 422
        return response
    if not request.user.is_verified:
        response = JsonResponse({'status' : 'error', 'msg': 'You cannot order without verifying your email', 'profile': True })
        response.status_code = 422
        return response
    if not request.user.phone or request.user.phone == '' :
        response = JsonResponse({'status' : 'error', 'msg': 'You cannot order without having a phone number', 'profile': True })
        response.status_code = 422
        return response

    cart = get_cart(request)
    if len(cart) > 0:
        # create an order
        order = Order(user=request.user)
        order.shipping_address = request.user.shipping_addresses.filter(is_default=True).first()
        orders = []
        for item in cart:
            # create order_items
            order_item = OrderItem(product_id=item.product_id,
                quantity=item.quantity, price_per_unit=item.product.price_per_unit
            )
            orders.append(order_item)
            product = Product.objects.get(pk=item.product_id)
            if product.quantity == 0:
                response = JsonResponse({'status' : 'error',
                    'msg': '#Item {} is out of stock'.format(product.name),
                    'out_of_stock': True, 'qty': 'qty_{}'.format(product.pk)  })
                response.status_code = 422
                return response
            if product.quantity < int(order_item.quantity):
                response = JsonResponse({'status' : 'error',
                    'msg': 'There are only {} {} left, please change the quantity'\
                    .format(product.quantity, product.name),
                    'quantity': True, 'qty': 'qty_{}'.format(product.pk) })
                response.status_code = 422
                return response

        order.save()
        # save the orders
        for item in orders:
            # increase sales count of the product
            product = item.product
            product.orders_count += int(item.quantity)
            product.quantity -= int(item.quantity)
            product.save()
            item.order = order
            item.save()

        # send mail to the customers
        subject = 'You Just Placed an Order from Tetris'
        message = ''
        from_email = settings.DEFAULT_FROM_EMAIL or 'Tetris Retails <noreply@tetrisretails.com>'
        recipient_list = (request.user.email,)
        html_message = loader.render_to_string(
          'emails/customer_order_list.html', {'order': order,'request':request},
        )
        send_mail(subject, message, from_email, recipient_list, fail_silently=True, html_message=html_message)

        # send mail to the admins
        subject = '{} Just Placed an Order from Tetris'.format(request.user.username)
        message = ''
        from_email = settings.DEFAULT_FROM_EMAIL or 'Tetris Retails <noreply@tetrisretails.com>'
        recipient_list = ()
        for admin in admins:
            recipient_list += (admin.email,)
        html_message = loader.render_to_string(
          'emails/customer_order_to_admin.html', {'order': order,'request':request},
        )
        send_mail(subject, message, from_email, recipient_list, fail_silently=True, html_message=html_message)

        # clear cart
        request.user.cart.all().delete()
        request.session['cart'] = []
        response = JsonResponse({'status' : 'success', 'msg': 'order successfully made' })
        response.status_code = 200
        return response
    response = JsonResponse({'status' : 'error', 'msg': 'your cart is empty' })
    response.status_code = 422
    return response

@csrf_exempt
@login_required(login_url='/login/')
def remove_shipping_address(request):
    shipping_address = ShippingAddress.objects.filter(user = request.user, pk = request.POST['shipping_id']).first()
    if not shipping_address.orders.exists():
        shipping_address.delete()
        response = JsonResponse({'status' : 'success', 'msg': 'removed successfully' })
        response.status_code = 200
        return response
    response = JsonResponse({'status' : 'error', 'msg': 'you cannot delete this shipping address. An order is shipping to it' })
    response.status_code = 422
    return response

@csrf_exempt
@login_required(login_url='/login/')
def customer_cancel_order(request):
    if not request.POST.get('reason') or request.POST['reason'].strip() == '':
        response = JsonResponse({'status' : 'error', 'msg': 'Please enter a reason' })
        response.status_code = 422
        return response
    order = Order.objects.filter(ref=request.POST['order_ref'], user=request.user).first()
    if order:
        order.status = 'cancelled'
        order.reason_cancelled = request.POST['reason'].strip()
        order.canceller = request.user
        order.save()

        # increase stock
        for item in order.order_items.all():
            # increase sales count of the product
            product = item.product
            product.orders_count -= int(item.quantity)
            product.quantity += int(item.quantity)
            product.save()

        # send mail to the admins
        subject = '{} Just Cancelled an Order from Tetris'.format(request.user.username)
        message = ''
        from_email = settings.DEFAULT_FROM_EMAIL or 'Tetris Retails <noreply@tetrisretails.com>'
        recipient_list = ()
        for admin in admins:
            recipient_list += (admin.email,)
        html_message = loader.render_to_string(
          'emails/customer_cancel_order_to_admin.html', {'order': order,'request':request},
        )
        send_mail(subject, message, from_email, recipient_list, fail_silently=True, html_message=html_message)

        # send mail to the customers
        subject = 'You Have Cancelled Order {} from Tetris'.format(order.ref)
        message = ''
        from_email = settings.DEFAULT_FROM_EMAIL or 'Tetris Retails <noreply@tetrisretails.com>'
        recipient_list = (request.user.email,)
        html_message = loader.render_to_string(
          'emails/customer_cancel_order.html', {'order': order,'request':request},
        )
        send_mail(subject, message, from_email, recipient_list, fail_silently=True, html_message=html_message)


        response = JsonResponse({'status' : 'success', 'msg': 'Order cancelled successfully' })
        response.status_code = 200
        return response
    response = JsonResponse({'status' : 'error', 'msg': 'an error occured. please try again later' })
    response.status_code = 422
    return response

@csrf_exempt
@login_required(login_url='/login/')
def customer_confirm_delivery(request):
    if not request.POST.get('order_ref'):
        response = JsonResponse({'status' : 'error', 'msg': 'the order reference is needed' })
        response.status_code = 422
        return response
    order = Order.objects.filter(ref=request.POST['order_ref'], user=request.user).first()
    if order:
        order.confirm_delivery_date = datetime.now()
        order.status = 'delivered'
        order.save()
        for order_item in order.order_items.all():
            order_item.product.num_deliveries += 1
            order_item.product.save()

        # send mail to the customers
        subject = 'You Have Confirmed Delivery of Order {} from Tetris'.format(order.ref)
        message = ''
        from_email = settings.DEFAULT_FROM_EMAIL or 'Tetris Retails <noreply@tetrisretails.com>'
        recipient_list = (request.user.email,)
        html_message = loader.render_to_string(
          'emails/customer_confirm_delivery.html', {'order': order,'request':request},
        )
        send_mail(subject, message, from_email, recipient_list, fail_silently=False, html_message=html_message)

        # send mail to the admins
        subject = '{} Just Confirmed the Delivery of Order {}'\
            .format(request.user.username, order.ref)
        message = ''
        from_email = settings.DEFAULT_FROM_EMAIL or 'Tetris Retails <noreply@tetrisretails.com>'
        recipient_list = ()
        for admin in admins:
            recipient_list += (admin.email,)
        html_message = loader.render_to_string(
          'emails/customer_confirm_order_to_admin.html', {'order': order,'request':request},
        )
        send_mail(subject, message, from_email, recipient_list, fail_silently=False, html_message=html_message)

        response = JsonResponse({'status' : 'success', 'msg': 'Order delivery confirmed successfully' })
        response.status_code = 200
        return response

def verify_email(request, email_token):
    # uid = force_text(urlsafe_base64_decode(uidb64))
    user = User.objects.filter(email_token=email_token).first()
    context = {'verified': False}
    if user:
        if user.is_verified == True:
            context['verified'] = True
        elif user.email_token == email_token:
            user.is_verified = True
            user.save()
            context['verified'] = True
    return render(request, 'emails/verify_account.html', context)

@login_required(login_url='/login/')
def resend_verification(request):
    # uid = force_text(urlsafe_base64_decode(uidb64))
    user = request.user
    context = {}
    if user.is_verified == False:
        # send user account verification email
        subject = 'Verify Your Tetris Account'
        message = ''
        from_email = settings.DEFAULT_FROM_EMAIL or 'Tetris Retails <noreply@tetrisretails.com>'
        recipient_list = (user.email, )
        html_message = loader.render_to_string(
        'emails/account_verification_email.html', {'user': user,'request':request},
        )
        send_mail(subject, message, from_email, recipient_list, fail_silently=True, html_message=html_message)
    return redirect('/profile')

def page_not_found(request):
  return render(request, 'store/pages/error/404.html')

def internal_server_error(request):
  return render(request, 'store/pages/error/500.html')

def handle_email(request):
    user = request.user
    return render(request, 'emails/account_verification_email.html', {'user': user, 'request':request})