# Tetris template tags and filters

# from .collections import Collections
from django import template

register = template.Library()
data = {}

# return correct format of phone number
@register.filter(name='phone_num')
def phone_num(string):
	return string[1:]