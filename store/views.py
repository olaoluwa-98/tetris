from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from .collections import Collections
# from .serializers import *
from .models import *
from .forms import *

col = Collections()

# def get_cart(session, user=None):
#     if user is None:




class IndexView(ListView):
    model = Product
    template_name = 'store/pages/index.html'

    # this retrieves data that'll be displayed in the index page
    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        # get cart items from session too
        context['popular_products'] = col.popular_products(6)
        context['popular_brands'] = col.popular_brands(4)
        context['cart'] = []
        if self.request.user.is_authenticated:
            context['wish_list'] = self.request.user.get_wish()
            context['cart'] = self.request.user.get_cart()
        return context


class CustomerCareView(IndexView):
    template_name = 'store/pages/customer_care.html'

    def get_context_data(self, **kwargs):
        context = {}
        # get cart items from session too
        context['cart'] = []
        if self.request.user.is_authenticated:
            context['wish_list'] = self.request.user.get_wish()
            context['cart'] = self.request.user.get_cart()
        return context


class AboutView(IndexView):
    template_name = 'store/pages/about.html'

    def get_context_data(self, **kwargs):
        context = {}
        # get cart items from session too
        context['cart'] = []
        if self.request.user.is_authenticated:
            context['wish_list'] = self.request.user.get_wish()
            # get cart items from session too
            context['cart'] = self.request.user.get_cart()
        return context


class CartView(ListView):
    model = Cart
    # queryset = Cart.objects.filter(user_id=self.request.user.id).order_by('-created_at')
    context_object_name = 'products'
    template_name = 'store/pages/cart.html'
    success_url = '/store/'

    def get_context_data(self, **kwargs):
        # context = [super(CartView, self).get_context_data(**kwargs)]
        context = {}
        # get cart items from session too
        context['cart'] = []
        if self.request.user.is_authenticated:
            context['wish_list'] = self.request.user.get_wish()
            context['cart'] = self.request.user.get_cart()
        return context


class WishListView(LoginRequiredMixin, ListView):
    model = Wish
    # queryset = Cart.objects.filter(user_id=self.request.user.id).order_by('-created_at')
    context_object_name = 'products'
    template_name = 'store/pages/wish_list.html'
    success_url = '/store/'

    def get_context_data(self, **kwargs):
        # context = [super(CartView, self).get_context_data(**kwargs)]
        context = {}
        # get cart items from session too
        context['wish_list'] = self.request.user.get_wish()
        context['cart'] = self.request.user.get_cart()
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
        # get cart items from session too
        context['cart'] = []
        if self.request.user.is_authenticated:
            context['wish_list'] = self.request.user.get_wish()
            context['cart'] = self.request.user.get_cart()
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
        # get cart items from session too
        context['cart'] = []
        if self.request.user.is_authenticated:
            context['wish_list'] = self.request.user.get_wish()
            context['cart'] = self.request.user.get_cart()
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
        # get cart items from session too
        context['cart'] = []
        if self.request.user.is_authenticated:
            context['wish_list'] = self.request.user.get_wish()
            context['cart'] = self.request.user.get_cart()
        return context


class ProfileView(LoginRequiredMixin, ListView):
    model = get_user_model()
    # queryset = Cart.objects.filter(user_id=self.request.user.id).order_by('-created_at')
    context_object_name = 'user_details'
    template_name = 'store/pages/profile.html'
    success_url = '/store/'

    def post(self, request, *args, **kwargs):
        form = ProfileForm(request.POST or None, request.user)
        context = {'form': form}
        # get cart items from session
        context['cart'] = []
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
        # context = [super(CartView, self).get_context_data(**kwargs)]
        context = {}
        # get cart items from session too
        context['wish_list'] = self.request.user.get_wish()
        context['cart'] = self.request.user.get_cart()
        return context


def handle_login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')
    form = LoginForm(request.POST or None)
    if form.is_valid():
        user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(request.POST['redirect_url'])
    context = {'form': form}
    # get cart items from session
    context['cart'] = []
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
            return HttpResponseRedirect(request.POST['redirect_url'])
    context = {'form': form}
    # get cart items from session
    context['cart'] = []
    return render(request, 'registration/register.html', context)


@login_required(login_url='/login/')
def handle_logout(request):
    logout(request)
    return HttpResponseRedirect('/login')


@csrf_exempt
def add_to_cart(request):
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

    else:
        cart = request.session['cart']
        product_id = request.POST['product_id']
        qty = request.POST['quantity']

        response = JsonResponse({'status' : 'success', 'msg': 'added successfully' })
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
def empty_cart(request):
    if request.user.is_authenticated:
        carts = Cart.objects.filter(user_id=request.user.id)
        for cart in carts:
            cart.delete()
        if request.session.get('cart'):
            request.session['cart'] = ''
        response = JsonResponse({'status' : 'success', 'msg': 'cart emptied' })
        response.status_code = 200
        return response

    if request.session.get('cart'):
        request.session['cart'] = ''
    response = JsonResponse({'status' : 'success', 'msg': 'cart emptied' })
    response.status_code = 200
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