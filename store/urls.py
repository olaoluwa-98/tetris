from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import (
        PasswordChangeView,
        PasswordChangeDoneView,
        PasswordResetView,
        PasswordResetDoneView,
        PasswordResetConfirmView,
        PasswordResetCompleteView
    )
from django.urls import reverse_lazy
from .views import *

app_name = 'store'

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^about/$', AboutView.as_view(), name='about'),
    url(r'^add-to-cart', add_to_cart, name ="add_to_cart"),
    url(r'^add-to-wish-list', add_to_wish_list, name ="add_to_wish_list"),
    url(r'^brand/(?P<slug>[\w-]+)/$', BrandDetailView.as_view(), name='brand'),
    url(r'^cart/$', CartView.as_view(), name='cart'),
    url(r'^customer-care/$', CustomerCareView.as_view(), name='customer_care'),
    url(r'^empty-cart', empty_cart, name ="empty_cart"),
    url(r'^empty-wish-list', empty_wish_list, name ="empty_wish_list"),
    url(r'^profile/$', ProfileView.as_view(), name='profile'),
    url(r'^product/(?P<slug>[\w-]+)/$', ProductDetailView.as_view(), name='product'),
    url(r'^remove-from-wish-list', remove_from_wish_list, name ="remove_from_wish_list"),
    url(r'^remove-from-cart', remove_from_cart, name ="remove_from_cart"),
    url(r'^store/$', StoreView.as_view(), name='store'),
    url(r'^store/men/$', MenStoreView.as_view(), name='men'),
    url(r'^store/women/$', WomenStoreView.as_view(), name='women'),
    url(r'^wish-list/$', WishListView.as_view(), name='wish_list'),



    # auth
    url(r'^login/$', handle_login, name='login'),
    url(r'^logout/$', handle_logout, name='logout'),
    url(r'^register/$', handle_register, name='register'),

    # change password and reset password
    url(r'^password-change/$', PasswordChangeView.as_view(success_url=reverse_lazy('store:password_change_done')), name='password_change'),
    url(r'^password-change/done/$', PasswordChangeDoneView.as_view(), name='password_change_done'),
    url(r'^password-reset/$', PasswordResetView.as_view(success_url=reverse_lazy('store:password_reset_done')), name='password_reset'),
    url(r'^password-reset/done/$', PasswordResetDoneView.as_view(), name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    url(r'^reset/done/$', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)