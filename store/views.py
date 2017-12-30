from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
# from .serializers import *
from .models import *
from .forms import *

class IndexView(ListView):
    model = Product
    # get products that are 1 or more in store
    queryset = Product.objects.filter(quantity__gte=1).order_by('-created_at')[:5]
    context_object_name = 'products'
    template_name = 'store/index.html'

    # this retrieves data that'll be displayed in the index page
    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['wish_list'] = []
        context['cart'] = []
        if self.request.user.is_authenticated:
            context['wish_list'] = self.request.user.get_wish()
            context['cart'] = self.request.user.get_cart()
        return context

    # def get(self, request, *args, **kwargs):
    #     return render(request, self.template_name, {'products': self.queryset, ''})

class AboutView(IndexView):
    template_name = 'store/about.html'

    def get_context_data(self, **kwargs):
        context = {}
        context['wish_list'] = []
        context['cart'] = []
        if self.request.user.is_authenticated:
            context['wish_list'] = self.request.user.get_wish()
            context['cart'] = self.request.user.get_cart()
        return context

class StoreView(LoginRequiredMixin, ListView):
    model = Product
    # get products that are 1 or more in store
    queryset = Product.objects.filter(quantity__gte=1).order_by('-created_at')[:5]
    context_object_name = 'products'
    template_name = 'store/store.html'
    success_url = '/store'
    login_url = '/login'

    # this retrieves data that'll be displayed in the index page
    def get_context_data(self, **kwargs):
        context = super(StoreView, self).get_context_data(**kwargs)
        context['wish_list'] = self.request.user.get_wish()
        context['cart'] = self.request.user.get_cart()
        return context

def handle_login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/store')
    form = LoginForm(request.POST or None)
    if form.is_valid():
        user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
        if user is not None:
            login(request, user)
            HttpResponseRedirect('/store')
    return render(request, 'registration/login.html', {'form': form})

def handle_register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/store')
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        user.refresh_from_db()  # load the profile instance created by the signal
        user.save()
        user = authenticate(username=user.username, password=form.cleaned_data.get('password1'))
        if user is not None:
            login(request, user)
            HttpResponseRedirect('/store')
    return render(request, 'registration/register.html', {'form': form})

@login_required(login_url='/login/')
def handle_logout(request):
    logout(request)
    return HttpResponseRedirect('/')