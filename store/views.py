from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .collections import Collections
# from .serializers import *
from .models import *
from .forms import *

col = Collections()

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