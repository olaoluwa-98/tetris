from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from .collections import Collections
# from .serializers import *
from .models import *
from .forms import *

col = Collections()

def get_cart(request):
    # request.session['cart_item_ids'] = ''
    if request.session.get('cart_item_ids'):
        cart = request.session['cart_item_ids'].split('-')[1:]
        cart_item_ids = []
        real_cart = [Cart(product_id= int(cart[0][0])  , quantity= int(cart[0][2]))]
        for x in range(1, len(cart) - 1):
            real_cart.append( Cart(product_id= int(cart[x][0])  , quantity= int(cart[x][2])) )
        if request.user.is_authenticated:
            cart_from_db_ids = [x.product_id for x in request.user.get_cart()]
            real_cart = [ x for x in real_cart if x.product_id not in cart_from_db_ids]
            real_cart += list(request.user.get_cart())
        return real_cart
    elif request.user.is_authenticated:
        return request.user.get_cart()


class IndexView(ListView):
    model = Product
    template_name = 'store/pages/index.html'

    # this retrieves data that'll be displayed in the index page
    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['popular_products'] = col.popular_products(6)
        context['popular_brands'] = col.popular_brands(4)
        context['cart'] = get_cart(self.request)
        if self.request.user.is_authenticated:
            context['wish_list'] = self.request.user.get_wish()
        return context


class CustomerCareView(IndexView):
    template_name = 'store/pages/customer_care.html'

    def get_context_data(self, **kwargs):
        context = {}
        context['cart'] = get_cart(self.request)
        if self.request.user.is_authenticated:
            context['wish_list'] = self.request.user.get_wish()
        return context


class AboutView(IndexView):
    template_name = 'store/pages/about.html'

    def get_context_data(self, **kwargs):
        context = {}
        context['cart'] = get_cart(self.request)
        if self.request.user.is_authenticated:
            context['wish_list'] = self.request.user.get_wish()
        return context


class CartView(ListView):
    model = Cart
    template_name = 'store/pages/cart.html'

    def get_context_data(self, **kwargs):
        context = {}
        context['cart'] = get_cart(self.request)
        if self.request.user.is_authenticated:
            context['wish_list'] = self.request.user.get_wish()
        return context


class WishListView(LoginRequiredMixin, ListView):
    model = Wish
    template_name = 'store/pages/wish_list.html'
    success_url = '/store/'

    def get_context_data(self, **kwargs):
        context = {}
        context['cart'] = get_cart(self.request)
        context['wish_list'] = self.request.user.get_wish()
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'store/pages/product_detail.html'
    def get_context_data(self, **kwargs):
        product = Product.objects.get(slug=self.kwargs['slug'])
        context = { 'product': product}
        context['related_products'] = col.related_products(product, 4)
        context['cart'] = get_cart(self.request)
        if self.request.user.is_authenticated:
            context['wish_list'] = self.request.user.get_wish()
        return context


class BrandDetailView(DetailView):
    model = Brand
    template_name = 'store/pages/brand.html'
    def get_context_data(self, **kwargs):
        brand = Brand.objects.get(slug=self.kwargs['slug'])
        context = { 'brand': brand}
        context['cart'] = get_cart(self.request)
        if self.request.user.is_authenticated:
            context['wish_list'] = self.request.user.get_wish()
        return context


class StoreView(ListView):
    model = Product
    # get products that are 1 or more in store
    queryset = Product.objects.filter(quantity__gte=1).order_by('-created_at')[:5]
    context_object_name = 'products'
    template_name = 'store/pages/store.html'
    success_url = '/store/'

    def get_context_data(self, **kwargs):
        context = super(StoreView, self).get_context_data(**kwargs)
        context['popular_products'] = col.popular_products(6)
        context['popular_brands'] = col.popular_brands(4)
        context['latest_products'] = col.latest_products(6)
        context['categories'] = col.categories(4)
        context['cart'] = get_cart(self.request)
        if self.request.user.is_authenticated:
            context['wish_list'] = self.request.user.get_wish()

        return context


class MenStoreView(ListView):
    model = Product
    # get products that are 1 or more in store
    queryset = Product.objects.filter(quantity__gte=1, gender='male').order_by('-created_at')[:5]
    context_object_name = 'products'
    template_name = 'store/pages/men.html'
    success_url = '/store/'

    def get_context_data(self, **kwargs):
        context = super(MenStoreView, self).get_context_data(**kwargs)
        context['cart'] = get_cart(self.request)
        if self.request.user.is_authenticated:
            context['wish_list'] = self.request.user.get_wish()

        return context


class WomenStoreView(ListView):
    model = Product
    # get products that are 1 or more in store
    queryset = Product.objects.filter(quantity__gte=1, gender='female').order_by('-created_at')[:5]
    context_object_name = 'products'
    template_name = 'store/pages/women.html'
    success_url = '/store/'

    def get_context_data(self, **kwargs):
        context = super(WomenStoreView, self).get_context_data(**kwargs)
        context['cart'] = get_cart(self.request)
        if self.request.user.is_authenticated:
            context['wish_list'] = self.request.user.get_wish()

        return context


class ProfileView(LoginRequiredMixin, ListView):
    model = get_user_model()
    template_name = 'store/pages/profile.html'
    success_url = '/store/'

    def post(self, request, *args, **kwargs):
        form = ProfileForm(request.POST or None, request.user)
        context = {'form': form}

        context['cart'] = get_cart(self.request)
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
        context['cart'] = get_cart(self.request)
        context['wish_list'] = self.request.user.get_wish()
        return context


def handle_login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')
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
            return HttpResponseRedirect(request.POST['redirect_url'])
    context = {'form': form}
    context['cart'] = get_cart(request)
    return render(request, 'registration/login.html', context)


def handle_register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')
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
            return HttpResponseRedirect(request.POST['redirect_url'])
    context = {'form': form}
    context['cart'] = get_cart(request)
    return render(request, 'registration/register.html', context)


@login_required(login_url='/login/')
def handle_logout(request):
    logout(request)
    return HttpResponseRedirect('/login')


@csrf_exempt
def add_to_cart(request):
    if request.session.get('cart_item_ids'):
        if request.POST['product_id'] + 'x' in request.session.get('cart_item_ids'):
            product = request.POST['product_id'] + 'x'
            cart = request.session.get('cart_item_ids')
            index = cart.find(product)
            new_qty = int(cart[ index + 2]) + int(request.POST['quantity'])
            request.session['cart_item_ids'] = cart.replace(product + cart[ index + 2], \
                product + str(new_qty))
        else:
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
def remove_from_cart(request):
    if request.session.get('cart_item_ids'):
        product = '-' + request.POST['product_id'] + 'x'
        cart = request.session.get('cart_item_ids')

        index = cart.find(product)
        request.session['cart_item_ids'] = cart.replace(product + cart[ index + 3], '')
        print (request.session['cart_item_ids'])
    if request.user.is_authenticated:
        cart_item = Cart.objects.filter(user = request.user, product_id = request.POST['product_id'])
        cart_item.delete()
        response = JsonResponse({'status' : 'success', 'msg': 'removed successfully' })
        response.status_code = 200
        return response
    response = JsonResponse({'status' : 'error', 'msg': 'error occured, please try again later.' })
    response.status_code = 402
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