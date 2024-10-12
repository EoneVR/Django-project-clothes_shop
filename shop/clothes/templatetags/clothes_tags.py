from django import template
from clothes.models import Category, Tag, Brand, Size, Color, WishList

register = template.Library()


@register.simple_tag()
def get_categories():
    return Category.objects.all()


@register.simple_tag()
def get_tags():
    return Tag.objects.all()


@register.simple_tag()
def get_brands():
    return Brand.objects.all()


@register.simple_tag()
def get_sorties():
    return [
        ('title', 'Name (A - Z)'),
        ('-title', 'Name (Z - A)'),
        ('price', 'Price (Low-High)'),
        ('-price', 'Price (High-Low)'),
    ]


@register.simple_tag()
def query_transform(request, key, value):
    updated = request.GET.copy()
    updated[key] = value
    return updated.urlencode()


@register.simple_tag()
def check_wishlist(request, pk):
    return WishList.objects.filter(product_id=pk, user=request.user).exists()