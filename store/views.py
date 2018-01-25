from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.views.generic import ListView, DetailView
from django.views.generic.base import RedirectView
# from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt#, csrf_protect
from .collections import Collections
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import *
from .forms import *
from .addresses import STATES

col = Collections()

def get_cart(request):
    # request.session['cart_item_ids'] = ''
    # import pdb; pdb.set_trace()
    if request.session.get('cart_item_ids'):
        cart = request.session['cart_item_ids'].split('-')[1:]
        real_cart = []
        for x in range(0, len(cart)):
            real_cart.append(Cart(product_id=int(cart[x][0]),quantity=int(cart[x][2])) )
        if request.user.is_authenticated:
            cart_from_db_ids = [x.product_id for x in request.user.cart.all()]
            real_cart = [ x for x in real_cart if x.product_id not in cart_from_db_ids]
            real_cart += list(request.user.cart.all())
        return real_cart
    elif request.user.is_authenticated:
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


class IndexView(ListView):
    model = Product
    template_name = 'store/pages/index.html'

    def get_context_data(self, **kwargs):
        context = {'popular_products':col.popular_products(6)}
        context['popular_brands'] = col.popular_brands(4)
        context['cart_count'] = len(get_cart(self.request))
        if self.request.user.is_authenticated:
            context['wish_list_count'] = self.request.user.wishes.count()
        return context


class CustomerCareView(ListView):
    template_name = 'store/pages/customer_care.html'

    def get_context_data(self, **kwargs):
        context = {}
        context['cart_count'] = len(get_cart(self.request))
        if self.request.user.is_authenticated:
            context['wish_list_count'] = self.request.user.wishes.count()
        return context


class AboutView(IndexView):
    template_name = 'store/pages/about.html'

    def get_context_data(self, **kwargs):
        context = {}
        context['cart_count'] = len(get_cart(self.request))
        if self.request.user.is_authenticated:
            context['wish_list_count'] = self.request.user.wishes.count()
        return context


class CartView(ListView):
    model = Cart
    template_name = 'store/pages/cart.html'

    def get_context_data(self, **kwargs):
        context = {}
        page = self.request.GET.get('page')
        cart = get_cart(self.request)
        cart_list = paginate(cart, page, 5)
        context['cart_list'] = cart_list
        context['cart_count'] = len(get_cart(self.request))
        if self.request.user.is_authenticated:
            context['wish_list_count'] = self.request.user.wishes.count()
        return context


class CheckoutView(LoginRequiredMixin, ListView):
    model = Cart
    template_name = 'store/pages/checkout.html'
    success_url = '/store/'

    def get_context_data(self, **kwargs):
        context = {}
        context['cart'] = get_cart(self.request)
        context['cart_count'] = len(get_cart(self.request))
        context['wish_list_count'] = self.request.user.wishes.count()
        return context


class WishListView(LoginRequiredMixin, ListView):
    model = Wish
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


class OrdersView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'store/pages/orders.html'
    success_url = '/store/'

    def get_context_data(self, **kwargs):
        page = self.request.GET.get('page')
        orders = paginate(self.request.user.orders.all(), page, 5)
        context = {'orders': orders}
        context['cart_count'] = len(get_cart(self.request))
        context['wish_list_count'] = self.request.user.wishes.count()
        return context

class OrderDetailView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'store/pages/order_detail.html'
    def get_context_data(self, **kwargs):
        orders = Order.objects.filter(user= self.request.user, ref=self.kwargs['ref'])
        order = None
        if orders.exists():
            order = orders.first()
        context = { 'order': order}
        page = self.request.GET.get('page')
        order_items = paginate(order.order_items.all(), page, 5)
        context['order_items'] = order_items
        context['cart_count'] = len(get_cart(self.request))
        if self.request.user.is_authenticated:
            context['wish_list_count'] = self.request.user.wishes.count()
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = 'store/pages/product_detail.html'
    def get_context_data(self, **kwargs):
        product = Product.objects.get(slug=self.kwargs['slug'])
        context = { 'product': product}
        context['related_products'] = col.related_products(product, 4)
        context['cart_count'] = len(get_cart(self.request))
        if self.request.user.is_authenticated:
            context['wish_list_count'] = self.request.user.wishes.count()
        return context


class ProductsView(ListView):
    model = Product
    queryset = Product.objects.all()
    template_name = 'store/pages/products.html'
    success_url = '/store/'

    def get_context_data(self, **kwargs):
        product_list = Product.objects.all().order_by('-created_at')
        page = self.request.GET.get('page')
        products = paginate(product_list, page, 10)
        context = {'products':products}
        context['cart_count'] = len(get_cart(self.request))
        if self.request.user.is_authenticated:
            context['wish_list_count'] = self.request.user.wishes.count()
        return context


class BrandDetailView(DetailView):
    model = Brand
    template_name = 'store/pages/brand_detail.html'
    def get_context_data(self, **kwargs):
        brand = Brand.objects.get(slug=self.kwargs['slug'])
        context = { 'brand': brand }
        context['popular_brand_products'] = col.popular_brand_products(brand, 6)
        context['latest_brand_products'] = col.latest_brand_products(brand, 8)
        context['cart_count'] = len(get_cart(self.request))
        if self.request.user.is_authenticated:
            context['wish_list_count'] = self.request.user.wishes.count()
        return context


class StoreView(ListView):
    model = Product
    queryset = Product.objects.all()
    template_name = 'store/pages/store.html'
    success_url = '/store/'

    def get_context_data(self, **kwargs):
        context = {'popular_products':col.popular_products(6) }
        context['popular_brands'] = col.popular_brands(4)
        context['latest_products'] = col.latest_products(6)
        context['categories'] = col.categories(4)
        context['cart_count'] = len(get_cart(self.request))
        if self.request.user.is_authenticated:
            context['wish_list_count'] = self.request.user.wishes.count()
        return context


class MenStoreView(ListView):
    model = Product
    queryset = Product.objects.all()
    template_name = 'store/pages/men.html'
    success_url = '/store/'

    def get_context_data(self, **kwargs):
        context = { 'popular_products': col.popular_men_products(6) }
        product_list = Product.objects.filter(gender__in=['male', 'unisex'])
        page = self.request.GET.get('page')
        products = paginate(product_list, page, 10)
        context['categories'] = col.categories()
        context['cart_count'] = len(get_cart(self.request))
        context['products'] = products
        if self.request.user.is_authenticated:
            context['wish_list_count'] = self.request.user.wishes.count()
        return context


class WomenStoreView(ListView):
    model = Product
    queryset = Product.objects.all()
    template_name = 'store/pages/women.html'
    success_url = '/store/'

    def get_context_data(self, **kwargs):
        context = { 'popular_products': col.popular_women_products(6) }
        product_list = Product.objects.filter(gender__in=['female', 'unisex'])
        page = self.request.GET.get('page')
        products = paginate(product_list, page, 10)
        context['categories'] = col.categories()
        context['cart_count'] = len(get_cart(self.request))
        context['products'] = products
        if self.request.user.is_authenticated:
            context['wish_list_count'] = self.request.user.wishes.count()
        return context


class ProfileView(LoginRequiredMixin, ListView):
    model = get_user_model()
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


class ShippingAddressesView(LoginRequiredMixin, ListView):
    model = ShippingAddress
    template_name = 'store/pages/shipping_address_list.html'
    success_url = '/store/'

    def get_context_data(self, **kwargs):
        shipping_addresses = ShippingAddress.objects.filter(user = self.request.user)
        context = {'shipping_addresses':shipping_addresses}
        context['cart_count'] = len(get_cart(self.request))
        context['wish_list_count'] = self.request.user.wishes.count()
        return context


class NewShippingAddressView(LoginRequiredMixin, ListView):
    model = ShippingAddress
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


class ShippingAddressDetailView(LoginRequiredMixin, ListView):
    model = ShippingAddress
    template_name = 'store/pages/shipping_address_detail.html'
    success_url = '/store/'

    def post(self, request, *args, **kwargs):
        form = ShippingAddressForm(request.POST or None)
        context = {}
        context['cart_count'] = len(get_cart(self.request))
        context['wish_list_count'] = self.request.user.wishes.count()
        context['states'] = STATES
        if form.is_valid():
            num = int(self.kwargs['num'])
            shippings = ShippingAddress.objects.filter(user=request.user, is_default=True)
            shipping_address = ShippingAddress.objects.filter(user=request.user)[num - 1]
            if request.POST.get('is_default') and shippings.exists():
                shippings.update(is_default=False)
                shipping_address.is_default = True
            shipping_address.zip_code = form.cleaned_data['zip_code']
            shipping_address.address = form.cleaned_data['address']
            shipping_address.city = form.cleaned_data['city']
            shipping_address.state = form.cleaned_data['state']
            shipping_address.save()
            context['shipping_address'] = shipping_address
            context['success'] = 'Your shipping address has been updated'
            return render(request, 'store/pages/shipping_address_detail.html', context)
        context['form'] = form
        return render(request, 'store/pages/shipping_address_detail.html', context)

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
        import pdb; pdb.set_trace()
        if request.POST.get('is_default') and shippings.exists():
            shippings.update(is_default=False)
            shipping_address.is_default = True
        shipping_address.zip_code = form.cleaned_data['zip_code']
        shipping_address.address = form.cleaned_data['address']
        shipping_address.city = form.cleaned_data['city']
        shipping_address.state = form.cleaned_data['state']
        shipping_address.save()
        msg = 'Your shipping address has been updated'
        return redirect('/shipping-address/{0}/?msg={1}'.format(request.POST['shipping_address_num'], msg))
    msg = 'some information you provided is incorrect'
    return redirect('/shipping-address/{0}/?msg={1}'.format(request.POST['shipping_address_num'], msg))


def handle_login(request):
    if request.user.is_authenticated:
        return redirect('/')
    form = LoginForm(request.POST or None)
    if form.is_valid():
        user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
        if user is not None:
            login(request, user)
            if request.session.get('cart_item_ids'):
                cart = request.session['cart_item_ids'].split('-')[1:]
                for x in range(0, len(cart) - 1):
                    cart_item = Cart(user=user, product_id= int(cart[x][0])  , quantity= int(cart[x][2]))
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

        user = user = get_user_model()(username=username, email=email)
        user.set_password(form.cleaned_data['password'])
        user.save()
        user = authenticate(username=user.username, password=form.cleaned_data.get('password'))
        if user is not None:
            login(request, user)
            if request.session.get('cart_item_ids'):
                cart = request.session['cart_item_ids'].split('-')[1:]
                for x in range(0, len(cart) - 1):
                    cart_item = Cart(user=user, product_id= int(cart[x][0])  , quantity= int(cart[x][2]))
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
    if request.session.get('cart_item_ids'):
        # if request.POST['product_id'] + 'x' in request.session.get('cart_item_ids'):
        #     product = request.POST['product_id'] + 'x'
        #     cart = request.session.get('cart_item_ids')
        #     index = cart.find(product)
        #     new_qty = int(cart[ index + 2]) + int(request.POST['quantity'])
        #     request.session['cart_item_ids'] = cart.replace(product + cart[ index + 2], \
        #         product + str(new_qty))
        # else:
        request.session['cart_item_ids'] += '-{0}x{1}'.format(request.POST['product_id'], request.POST['quantity'])
    else:
        request.session['cart_item_ids'] = '-{0}x{1}'.format(request.POST['product_id'], request.POST['quantity'])
    if request.user.is_authenticated:
        cart_item = Cart(user_id=request.user.id, product_id=request.POST['product_id'], quantity=request.POST['quantity'])
        if cart_item:
            cart_item.save()
            response = JsonResponse({'status' : 'success', 'msg': 'added successfully' })
            response.status_code = 200
            return response

        response = JsonResponse({'status' : 'error', 'msg': 'error occured, please try again later.' })
        response.status_code = 402
        return response
    response = JsonResponse({'status' : 'success', 'msg': 'added successfully' })
    response.status_code = 200
    return response

@csrf_exempt
def change_cart_item_qty(request):
    if int(request.POST['new_quantity']) < 1:
        response = JsonResponse({'status' : 'error', 'msg': 'quantity less than 0' })
        response.status_code = 402
        return response

    if request.session.get('cart_item_ids'):
        if request.POST['product_id'] + 'x' in request.session.get('cart_item_ids'):
            product = request.POST['product_id'] + 'x'
            cart = request.session.get('cart_item_ids')
            index = cart.find(product)
            request.session['cart_item_ids'] = cart.replace(product + cart[ index + 2], \
                product + request.POST['new_quantity'])

            response = JsonResponse({'status' : 'success', 'msg': 'quantity changed successfully' })
            response.status_code = 200
            return response
        else:
            response = JsonResponse({'status' : 'error', 'msg': 'error occured, please try again later.' })
            response.status_code = 402
            return response
    if request.user.is_authenticated:
        cart_item = Cart.objects.filter(user=request.user, product_id=request.POST['product_id']).first()
        if cart_item:
            cart_item.quantity = request.POST['new_quantity']
            cart_item.save()
            response = JsonResponse({'status' : 'success', 'msg': 'quantity changed successfully' })
            response.status_code = 200
            return response
    response = JsonResponse({'status' : 'error', 'msg': 'error occured, please try again later.' })
    response.status_code = 402
    return response

@csrf_exempt
def remove_from_cart(request):
    if request.session.get('cart_item_ids'):
        product = '-' + request.POST['product_id'] + 'x'
        cart = request.session.get('cart_item_ids')

        index = cart.find(product)
        request.session['cart_item_ids'] = cart.replace(product + cart[ index + 3], '')
        print (request.session['cart_item_ids'])
    if request.user.is_authenticated:
        cart_item = Cart.objects.filter(user = request.user, product_id = request.POST['product_id'])
        if cart_item.exists():
            cart_item.delete()
            response = JsonResponse({'status' : 'success', 'msg': 'removed successfully' })
            response.status_code = 200
            return response
        else:
            response = JsonResponse({'status' : 'error', 'msg': 'error occured, please try again later.' })
            response.status_code = 402
            return response
    response = JsonResponse({'status' : 'success', 'msg': 'removed successfully' })
    response.status_code = 200
    return response

@csrf_exempt
@login_required(login_url='/login/')
def add_to_wish_list(request):
    wish_item = Wish(user_id=request.user.id, product_id=request.POST['product_id'])
    if wish_item:
        wish_item.save()
        response = JsonResponse({'status' : 'success', 'msg': 'added successfully' })
        response.status_code = 200
        return response

    response = JsonResponse({'status' : 'error', 'msg': 'error occured, please try again later.' })
    response.status_code = 402
    return response

@csrf_exempt
@login_required(login_url='/login/')
def remove_from_wish_list(request):
    wish_item = Wish.objects.filter(user = request.user, product_id = request.POST['product_id'])
    if wish_item:
        wish_item.delete()
        response = JsonResponse({'status' : 'success', 'msg': 'removed successfully' })
        response.status_code = 200
        return response

    response = JsonResponse({'status' : 'error', 'msg': 'error occured, please try again later.' })
    response.status_code = 402
    return response

@csrf_exempt
def empty_cart(request):
    if request.session.get('cart_item_ids'):
        request.session['cart_item_ids'] = ''
    if request.user.is_authenticated:
        carts = Cart.objects.filter(user_id=request.user.id)
        for cart in carts:
            cart.delete()
        if request.session.get('cart'):
            request.session['cart'] = ''
        response = JsonResponse({'status' : 'success', 'msg': 'cart emptied' })
        response.status_code = 200
        return response
    response = JsonResponse({'status' : 'error', 'msg': 'error occured, please try again later.' })
    response.status_code = 402
    return response

@csrf_exempt
@login_required(login_url='/login/')
def empty_wish_list(request):
        wishes = Wish.objects.filter(user_id=request.user.id)
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
        response.status_code = 402
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
        # clear cart
        request.user.cart.all().delete()
        request.session['cart_item_ids'] = ''
        response = JsonResponse({'status' : 'success', 'msg': 'order successfully made' })
        response.status_code = 200
        return response

        response = JsonResponse({'status' : 'error', 'msg': 'error occured, please try again later.' })
        response.status_code = 402
        return response
    response = JsonResponse({'status' : 'error', 'msg': 'your cart is empty' })
    response.status_code = 402
    return response

@csrf_exempt
@login_required(login_url='/login/')
def remove_shipping_address(request):
    shipping_address = ShippingAddress.objects.filter(user = request.user, pk = request.POST['shipping_id']).first()
    if not shipping_address.orders.all():
        shipping_address.delete()
        response = JsonResponse({'status' : 'success', 'msg': 'removed successfully' })
        response.status_code = 200
        return response

    response = JsonResponse({'status' : 'error', 'msg': 'you cannot delete this shipping_address. An order is shipping to it' })
    response.status_code = 402
    return response
