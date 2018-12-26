from django import template
from rango.models import Category

register = template.Library()

@register.inclusion_tag('rango/cats.html')
def get_category_list(starts_with, max_results = 0):
	
	category_list = []

	if starts_with :
		category_list = Category.objects.filter(name__istartswith = starts_with)

	else :
		category_list = Category.objects.all()
		return category_list	

	if max_results > 0 and len(category_list) > max_results:
		category_list = category_list[:max_results]

	return category_list

@register.inclusion_tag('rango/cats.html')
def get_all_categories():
	return ({'cats' : Category.objects.all()})		
		

