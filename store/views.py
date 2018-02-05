from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt#, csrf_protect
from .collections import Collections
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime
from .models import *
from .forms import *
from .addresses import STATES
from django.core.mail import send_mail

col = Collections()
User = get_user_model()
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
            request.session['cart'] = ''
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
        if self.request.user.is_authenticated:
            context['wish_list_count'] = self.request.user.wishes.count()
        return context


class CustomerCareView(TemplateView):
    template_name = 'store/pages/customer_care.html'

    def get_context_data(self, **kwargs):
        context = {}
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
        if self.request.user.is_authenticated:
            context['wish_list_count'] = self.request.user.wishes.count()
        return context


class CheckoutView(LoginRequiredMixin, TemplateView):
    template_name = 'store/pages/checkout.html'
    success_url = '/store/'

    def get_context_data(self, **kwargs):
        context = {}
        context['cart'] = get_cart(self.request)
        context['cart_count'] = len(get_cart(self.request))
        context['wish_list_count'] = self.request.user.wishes.count()
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
        context['wish_list_count'] = self.request.user.wishes.count()
        return context


class OrdersView(LoginRequiredMixin, TemplateView):
    template_name = 'store/pages/orders.html'
    success_url = '/store/'

    def get_context_data(self, **kwargs):
        page = self.request.GET.get('page')
        orders = paginate(self.request.user.orders.all(), page, 5)
        context = {'orders': orders}
        context['cart_count'] = len(get_cart(self.request))
        context['wish_list_count'] = self.request.user.wishes.count()
        return context

class OrderDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'store/pages/order_detail.html'
    success_url = '/store/'
    def get_context_data(self, **kwargs):
        orders = Order.objects.filter(user= self.request.user, ref=self.kwargs['ref'])
        order = None
        context = {}
        if orders.exists():
            order = orders.first()
            context['order'] = order
            page = self.request.GET.get('page')
            order_items = paginate(order.order_items.all(), page, 5)
            # import pdb; pdb.set_trace()
            if not order_items.object_list.exists():
                order_items = None
            context['order_items'] = order_items
        context['cart_count'] = len(get_cart(self.request))
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
        context['categories'] = col.categories(4)
        context['cart_count'] = len(get_cart(self.request))
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
        context['categories'] = col.categories()
        context['cart_count'] = len(get_cart(self.request))
        context['products'] = products
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
        context['categories'] = col.categories()
        context['cart_count'] = len(get_cart(self.request))
        context['products'] = products
        if self.request.user.is_authenticated:
            context['wish_list_count'] = self.request.user.wishes.count()
        return context


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'store/pages/profile.html'
    success_url = '/store/'

    def post(self, request, *args, **kwargs):
        form = ProfileForm(request.POST or None, request.user)
        context = {'form': form}

        context['cart_count'] = len(get_cart(self.request))
        if form.is_valid():
            user = request.user
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.username = form.cleaned_data['username']
            user.email = form.cleaned_data['email']
            user.phone = form.cleaned_data['phone']
            user.save()
            context['success'] = 'Your profile has been updated'
            return render(request, 'store/pages/profile.html', context)
        return render(request, 'store/pages/profile.html', context)

    def get_context_data(self, **kwargs):
        context = {}
        context['cart_count'] = len(get_cart(self.request))
        context['wish_list_count'] = self.request.user.wishes.count()
        return context


class CategoryView(TemplateView):
    template_name = 'store/pages/category.html'
    success_url = '/store/'

    def get_context_data(self, **kwargs):
        context = {'popular_products':col.popular_products(8) }
        context['latest_products'] = col.latest_products(8)
        context['categories'] = col.categories(4)
        context['cart_count'] = len(get_cart(self.request))
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
            shipping= ShippingAddress.objects.filter(user=request.user, is_default=True)
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
        return render(request, 'store/pages/new_shipping_address.html', context)

    def get_context_data(self, **kwargs):
        context = {}
        form = ShippingAddressForm(None)
        context['form'] = form
        context['states'] = STATES
        context['cart_count'] = len(get_cart(self.request))
        context['wish_list_count'] = self.request.user.wishes.count()
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
        return context

@login_required(login_url='/login/')
def update_shipping_address(request):
    form = ShippingAddressForm(request.POST or None)
    if form.is_valid():
        shippings = ShippingAddress.objects.filter(user=request.user, is_default=True, )
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
                    cart_item = Cart(user=user, product_id=cart_item['product_id'],quantity=cart_item['quantity'])
                    cart_item.save()
            return redirect(request.POST['redirect_url'])
    context = {'form': form}
    context['cart_count'] = len(get_cart(request))
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
        from_email = 'noreply@tetris.com'
        recipient_list = (user.email, )
        html_message = loader.render_to_string(
          'emails/account_verification_email.html', {'user': user,},
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
    return render(request, 'registration/register.html', context)


@login_required(login_url='/login/')
def handle_logout(request):
    logout(request)
    return redirect('/login')


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
        cart = Cart.objects.filter(user=request.user, product_id=request.POST['product_id'])
        if cart.exists():
            cart_item = cart.first()
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
        cart_item = Cart.objects.filter(user=request.user, product_id=request.POST['product_id'])
        if cart_item.exists():
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
    wish_item = Wish.objects.filter(user=request.user, product_id=request.POST['product_id'])
    if wish_item.exists():
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
        if cart.exists():
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
        for wish in wishes:
            wish.delete()
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
        response = JsonResponse({'status' : 'error', 'msg': 'You cannot order without verifying your email', 'email': True })
        response.status_code = 422
        return response

    cart = get_cart(request)
    if len(cart) > 0:
        # create an order
        order = Order(user=request.user)
        order.shipping_address = request.user.shipping_addresses.filter(is_default=True).first()
        order.save()
        for item in cart:
            # create order_items
            order_item = OrderItem(product_id=item.product_id,
                order=order, quantity=item.quantity, price_per_unit=item.product.price_per_unit
            )
            # increase sales count of the product
            product = Product.objects.get(pk=item.product_id)
            product.orders_count += 1
            product.save()
            order_item.save()

        # send mail to the customers
        subject = 'You Just Placed an Order from Tetris'
        message = ''
        from_email = 'noreply@tetris.lol'
        recipient_list = (request.user.email,)
        html_message = loader.render_to_string(
          'emails/customer_order_list.html', {'order': order,},
        )
        send_mail(subject, message, from_email, recipient_list, fail_silently=True, html_message=html_message)

        # clear cart
        request.user.cart.all().delete()
        request.session['cart'] = []
        response = JsonResponse({'status' : 'success', 'msg': 'order successfully made' })
        response.status_code = 200
        return response

        response = JsonResponse({'status' : 'error', 'msg': 'error occured, please try again later.' })
        response.status_code = 422
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
    if request.POST['reason'] == '':
        response = JsonResponse({'status' : 'error', 'msg': 'Please enter a reason' })
        response.status_code = 422
        return response
    order = Order.objects.filter(ref=request.POST['order_ref'], user=request.user)
    if order.exists():
        order = order.first()
        order.status = 'cancelled'
        order.reason_cancelled = request.POST['reason']
        order.canceller = request.user
        order.save()

        # send mail to the customers
        subject = 'You Have Cancelled Order {} from Tetris'.format(order.ref)
        message = ''
        from_email = 'noreply@tetris.lol'
        recipient_list = (request.user.email,)
        html_message = loader.render_to_string(
          'emails/customer_cancel_order.html', {'order': order,},
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
    orders = Order.objects.filter(ref=request.POST['order_ref'], user=request.user)
    if orders.exists():
        order = orders.first()
        order.confirm_delivery_date = datetime.now()
        order.status = 'delivered'
        order.save()
        for order_item in order.order_items.all():
            order_item.product.num_deliveries += 1
            order_item.product.save()

        # send mail to the customers
        subject = 'You Have Confirmed Delivery of Order {} from Tetris'.format(order.ref)
        message = ''
        from_email = 'noreply@tetris.lol'
        recipient_list = (request.user.email,)
        html_message = loader.render_to_string(
          'emails/customer_confirm_delivery.html', {'order': order,},
        )
        send_mail(subject, message, from_email, recipient_list, fail_silently=True, html_message=html_message)

        response = JsonResponse({'status' : 'success', 'msg': 'Order delivery confirmed successfully' })
        response.status_code = 200
        return response

def verify_email(request):
    uid = request.GET.get('uid')
    if User.objects.filter(id=uid).exists():
        user = User.objects.get(id=uid)
        user.is_verified = True
        user.save()
        context = {'verified': True}
    else:
        context = {'verified': False}
    return render(request, 'store/emails/verify_account.html', context)

def resend_verification(request):
    context = {}
    if request.method == 'POST':
        email = request.POST.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            if user.is_verified == False:
                # send user account verification email
                subject = 'Verify Your Tetris Account'
                message = ''
                from_email = 'noreply@tetris.com'
                recipient_list = (user.email, )
                html_message = loader.render_to_string(
                'emails/account_verification_email.html', {'user': user,},
                )
                send_mail(subject, message, from_email, recipient_list, fail_silently=True, html_message=html_message)
                context['verification_sent'] = True
            else:
                context['account_is_verified'] = True;
        else:
            context['email_not_found'] = True
    else:
        context['show_verification_form'] = True
    return render(request, 'resend-verification.html', data)

def page_not_found(request):
  return render(request, 'store/pages/error/404.html')

def internal_server_error(request):
  return render(request, 'store/pages/error/500.html')