from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('shop/', shop_view, name='shop'),
    path('product/<slug:slug>/', detail_product, name='product'),

    path('login/', login_view, name='login'),
    path('register/', register, name='register'),
    path('logout/', logout_view, name='logout'),

    path('save_review/<int:pk>/', save_review, name='save_review'),
    path('contact/', contact, name='contact'),
    path('wishlist_action/<int:pk>/', wishlist_action, name='wishlist_action'),
    path('wishlist/', wishlist, name='wishlist'),

    path('to_cart/<int:product_id>/', to_cart, name='to_cart'),
    path('plus_minus/<int:pk>/<str:action>/<str:color>/<str:size>/<int:quantity>/', plus_minus, name='plus_minus'),
    path('clear/', clear, name='clear'),
    path('cart/', cart, name='cart'),

    path('about/', about_us, name='about'),
    path('blog/', blog, name='blog'),
    path('search/', search, name='search'),

    path('checkout/', checkout, name='checkout'),
    path('process_checkout/', process_checkout, name='process_checkout'),
    path('success/', success_payment, name='success'),

    path('articles/', blog, name='article_list'),
    path('article/<int:pk>/', blog_detail, name='detail'),
    path('create_article/', create_article, name='create'),
    path('profile/<int:pk>/', profile_view, name='profile'),
    path('course/<int:pk>/update/', update_article, name='update'),
    path('course/<int:pk>/delete/', delete_article, name='delete'),
    path('profile/<int:pk>/edit/', update_profile, name='edit'),
    path('user/<int:pk>/edit/', update_user, name='edit_user'),
]
