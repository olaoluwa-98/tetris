# Tetris template tags and filters

# from .collections import Collections
from django import template
from store.models import Wish, Cart

register = template.Library()
data = {}

# return correct format of phone number
@register.filter(name='phone_num')
def phone_num(string):
	if string:
		return string[1:]
	return ''

# return true if user has the product wished
@register.filter(name='product_wished')
def product_wished(product_id, user):
	if user.is_authenticated():
		return Wish.objects.filter(product_id=product_id, user=user).exists()
	return False

# return true if user has the product carted
@register.filter(name='product_carted')
def product_carted(product_id, request):
	if request.user.is_authenticated:
		return Cart.objects.filter(product_id=product_id, user=request.user).exists()
	if request.session.get('cart_item_ids'):
		return str(product_id)+'x' in request.session['cart_item_ids']
	return False