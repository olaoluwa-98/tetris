from django.conf.urls import url
from django.conf import settings
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
    url(r'^cancel-order', customer_cancel_order, name ="customer_cancel_order"),
    url(r'^cart/$', CartView.as_view(), name='cart'),
    url(r'^category/(?P<slug>[\w-]+)/$', CategoryView.as_view(), name='category'),
    url(r'^checkout/$', CheckoutView.as_view(), name='checkout'),
    url(r'^confirm-delivery', customer_confirm_delivery, name ="customer_confirm_delivery"),
    url(r'^customer-care/$', CustomerCareView.as_view(), name='customer_care'),
    url(r'^change-cart-item-qty', change_cart_item_qty, name ="change_cart_item_qty"),
    url(r'^empty-cart', empty_cart, name ="empty_cart"),
    url(r'^empty-wish-list', empty_wish_list, name ="empty_wish_list"),
    url(r'^make-purchase', make_purchase, name ="make_purchase"),
    url(r'^new-shipping-address/$', NewShippingAddressView.as_view(), name='new_shipping_address'),
    url(r'^orders/$', OrdersView.as_view(), name='orders'),
    url(r'^order/(?P<ref>[\w]+)/$', OrderDetailView.as_view(), name='order'),
    url(r'^profile/$', ProfileView.as_view(), name='profile'),
    url(r'^products/$', ProductsView.as_view(), name='products'),
    url(r'^product/(?P<slug>[\w-]+)/$', ProductDetailView.as_view(), name='product'),
    url(r'^remove-from-cart', remove_from_cart, name ="remove_from_cart"),
    url(r'^remove-from-wish-list', remove_from_wish_list, name ="remove_from_wish_list"),
    url(r'^remove-shipping-address', remove_shipping_address, name ="remove_shipping_address"),
    url(r'^store/$', StoreView.as_view(), name='store'),
    url(r'^store/men/$', MenStoreView.as_view(), name='men'),
    url(r'^store/women/$', WomenStoreView.as_view(), name='women'),
    url(r'^shipping-address/(?P<num>[0-9]+)/$', ShippingAddressDetailView.as_view(), name='shipping_address'),
    url(r'^shipping-address-update/$', update_shipping_address, name='shipping_address_update'),
    url(r'^shipping-addresses/$', ShippingAddressesView.as_view(), name='shipping_addresses'),
    url(r'^wish-list/$', WishListView.as_view(), name='wish_list'),

    # auth
    url(r'^login/$', handle_login, name='login'),
    url(r'^logout/$', handle_logout, name='logout'),
    url(r'^register/$', handle_register, name='register'),
    # verify account email
    url(r'^verify/$', verify_email, name='verify_account'),
    url(r'^resend-verification/$', resend_verification, name='resend_verification'),

    # change password and reset password
    url(r'^password-change/$', PasswordChangeView.as_view(success_url=reverse_lazy('store:password_change_done')), name='password_change'),
    url(r'^password-change/done/$', PasswordChangeDoneView.as_view(), name='password_change_done'),
    url(r'^password-reset/$', PasswordResetView.as_view(success_url=reverse_lazy('store:password_reset_done')), name='password_reset'),
    url(r'^password-reset/done/$', PasswordResetDoneView.as_view(), name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    url(r'^reset/done/$', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]