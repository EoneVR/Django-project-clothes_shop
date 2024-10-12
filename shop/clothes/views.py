from django.contrib.auth import login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import ExpressionWrapper, F, FloatField
from django.core.paginator import Paginator
from django.views.generic import UpdateView

from .forms import LoginForm, RegisterForm, CommentFormAuthenticated, CommentFormAnonymous, ContactUsForm, AddToCartForm, DeliveryAddressForm, ArticleForm, EditProfileForm, EditUserForm
from .models import *
from django.urls import reverse, reverse_lazy
from .utils import CartForAuthenticatedUser
import stripe
from django.db import transaction

# Create your views here.


def index(request):
    tags = Tag.objects.all()
    products = Product.objects.order_by('-sales')[:6]
    articles = Article.objects.all()
    context = {
        'tags': tags,
        'products': products,
        'articles': articles
    }
    return render(request, 'clothes/index.html', context)


class ProductFilter:
    def __init__(self, request, queryset):
        self.request = request
        self.queryset = queryset

    def filter_by_category(self):
        category = self.request.GET.get('category')
        if category:
            self.queryset = self.queryset.filter(category__id=category)
        return self

    def filter_by_brand(self):
        brand = self.request.GET.get('brand')
        if brand:
            self.queryset = self.queryset.filter(brand__id=brand)
        return self

    def filter_by_tag(self):
        tag = self.request.GET.get('tag')
        if tag:
            self.queryset = self.queryset.filter(tags__id=tag)
        return self

    def sort_by(self):
        sort = self.request.GET.get('sort')
        if sort:
            self.queryset = self.queryset.order_by(sort)
        return self

    def paginate(self):
        page = self.request.GET.get('page', 1)
        paginator = Paginator(self.queryset, 12)
        return paginator.get_page(page)

    def filter_by_price(self):
        price = self.request.GET.get('price')

        self.queryset = self.queryset.annotate(
            discount_price=ExpressionWrapper(
                F('price') - F('price') * F('discount') / 100.0,
                output_field=FloatField()
            )
        )

        if price:
            if price == '0_50':
                self.queryset = self.queryset.filter(discount_price__lt=50)
            elif price == '50_100':
                self.queryset = self.queryset.filter(discount_price__gte=50, discount_price__lt=100)
            elif price == '100_150':
                self.queryset = self.queryset.filter(discount_price__gte=100, discount_price__lt=150)
            elif price == '150_200':
                self.queryset = self.queryset.filter(discount_price__gte=150, discount_price__lt=200)
            elif price == '200_250':
                self.queryset = self.queryset.filter(discount_price__gte=200, discount_price__lt=250)
            elif price == 'more_250':
                self.queryset = self.queryset.filter(discount_price__gt=250)

        return self

    def get_queryset(self):
        return self.queryset


def shop_view(request):
    products = Product.objects.all()
    product_filter = ProductFilter(request, products)
    products = (product_filter
                .filter_by_category()
                .filter_by_brand()
                .filter_by_tag()
                .filter_by_price()
                .sort_by()
                .get_queryset())
    paginated_products = product_filter.paginate()
    context = {
        'products': paginated_products
    }
    return render(request, 'clothes/shop.html', context)


def detail_product(request, slug):
    try:
        product = Product.objects.get(slug=slug)
        if request.user.is_authenticated:
            comment_form = CommentFormAuthenticated()
        else:
            comment_form = CommentFormAnonymous()
        comments = Comment.objects.filter(product=product)
        articles = Article.objects.all()
        form = AddToCartForm(product)
        sizes = product.sizes.all()
        colors = product.colors.all()
        context = {
            'form': form,
            'product': product,
            'sizes': sizes,
            'colors': colors,
            'comment_form': comment_form,
            'comments': comments,
            'articles': articles
        }
        return render(request, 'clothes/shop-details.html', context)
    except Exception as e:
        print(e)
        return render(request, 'clothes/index.html')


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user:
                login(request, user)
                try:
                    profile = Profile.objects.get(user=user)
                except:
                    Profile.objects.create(user=user)
                return redirect('index')
            else:
                return redirect('index')
        else:
            return redirect('index')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            return redirect('index')
        else:
            return redirect('index')


def logout_view(request):
    logout(request)
    return redirect('index')


def save_review(request, pk):
    if request.user.is_authenticated:
        form = CommentFormAuthenticated(request.POST, request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            product = Product.objects.get(pk=pk)
            comment.product = product
            comment.username = request.user.username
            comment.email = request.user.email
            comment.save()
            return redirect('product', product.slug)
    else:
        form = CommentFormAnonymous(request.POST, request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            product = Product.objects.get(pk=pk)
            comment.product = product
            comment.save()
            return redirect('product', product.slug)


def contact(request):
    if request.method == 'POST':
        form = ContactUsForm(data=request.POST)
        if form.is_valid():
            contactus = form.save()
            return redirect('contact')
    else:
        form = ContactUsForm()
    context = {
        'form': form
    }

    return render(request, 'clothes/contact.html', context)


def wishlist_action(request, pk):
    product = Product.objects.get(pk=pk)
    user = request.user
    if WishList.objects.filter(product=product, user=user).exists():
        wish = WishList.objects.get(product=product, user=user)
        wish.delete()
    else:
        WishList.objects.create(product=product, user=user)
    return redirect(request.META.get('HTTP_REFERER'))


def wishlist(request):
    user = request.user
    wishlists = WishList.objects.filter(user=user)
    products = [i.product for i in wishlists]
    context = {
        'products': products,
        'title': 'Wishlist'
    }
    return render(request, 'clothes/wishlist.html', context)


def to_cart(request, product_id):
    product = Product.objects.get(pk=product_id)
    if request.method == 'POST':
        form = AddToCartForm(data=request.POST, product=product)
        if form.is_valid():
            quantity = form.cleaned_data.get('quantity', 1)
            color = form.cleaned_data.get('color', None)
            if color:
                color = color.color.title
            else:
                color = 'No'
            size = form.cleaned_data.get('size', None)
            if size:
                size = size.size.title
            else:
                size = 'No'
            CartForAuthenticatedUser(request, product_id, 'add', color, size, quantity)
        else:
            print(form.errors)
    return redirect('product', product.slug)


def plus_minus(request, pk, action, color, size, quantity):
    if request.user.is_authenticated:
        CartForAuthenticatedUser(request, pk, action, color, size, quantity)
        return redirect('cart')


def cart(request):
    if request.user.is_authenticated:
        user_cart = CartForAuthenticatedUser(request)

        cart_info = user_cart.get_cart_info()
        print(cart_info)
        cart_info['title'] = 'My cart'
        return render(request, 'clothes/shopping-cart.html', cart_info)


def clear(request):
    if request.user.is_authenticated:
        user_cart = CartForAuthenticatedUser(request)
        user_cart.clear()
        return redirect('cart')


def about_us(request):
    return render(request, 'clothes/about.html')


def blog(request):
    articles = Article.objects.all()
    context = {
        'articles': articles,
        'title': 'All articles'
    }
    return render(request, 'clothes/blog.html', context)


def blog_detail(request, pk):
    article = Article.objects.get(pk=pk)
    context = {
        'title': f'Article: {article.title}',
        'article': article
    }
    return render(request, 'clothes/blog-details.html', context)


def create_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save()
            article.save()
            return redirect('detail', article.pk)
    else:
        form = ArticleForm()

    context = {
        'form': form,
        'title': 'Creating article'
    }
    return render(request, 'clothes/article_form.html', context)


def update_article(request, pk):
    article = get_object_or_404(Article, pk=pk)

    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            return redirect('blog-details', pk=article.pk)
    else:
        form = ArticleForm(instance=article)
    context = {
        'form': form,
        'title': 'Changing article',
    }
    return render(request, 'clothes/article_form.html', context)


def delete_article(request, pk):
    article = get_object_or_404(Article, pk=pk)

    if request.method == 'POST':
        article.delete()
        return redirect(reverse_lazy('index'))
    context = {
        'article': article,
    }
    return render(request, 'index', context)


def profile_view(request, pk):
    profile = get_object_or_404(Profile, user_id=pk)
    orders = Order.objects.filter(user=request.user).order_by('-placed_at')
    context = {
        'profile': profile,
        'orders': orders
    }
    return render(request, 'clothes/profile.html', context)


def update_profile(request, pk):
    profile = get_object_or_404(Profile, pk=pk)
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile', pk=profile.user.pk)
    else:
        form = EditProfileForm(instance=profile)

    context = {
        'form': form,
        'title': 'Change profile',
    }
    return render(request, 'clothes/article_form.html', context)


def update_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = EditUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile', pk=user.pk)
    else:
        form = EditUserForm(instance=user)

    context = {
        'form': form,
        'title': 'Change account',
    }
    return render(request, 'clothes/article_form.html', context)


def search(request):
    search_keyword = request.GET.get('searchKeyword')
    products = Product.objects.filter(title__icontains=search_keyword)
    context = {
        'products': products,
        'title': 'Product'
    }
    return render(request, 'clothes/shop.html', context)


def checkout(request):
    if request.user.is_authenticated:
        user_cart = CartForAuthenticatedUser(request)
        cart_info = user_cart.get_cart_info()
        context = {
            'delivery_form': DeliveryAddressForm(),
            'title': 'Placing an order',
            'cart_total_quantity': cart_info['cart_total_quantity'],
            'cart_total_price': cart_info['cart_total_price'],
            'order': cart_info['cart'],
            'products': cart_info['products']
        }
        return render(request, 'clothes/checkout.html', context)


def process_checkout(request):
    if request.method == 'POST':
        delivery_form = DeliveryAddressForm(data=request.POST)
        if delivery_form.is_valid():
            del_form = delivery_form.save(commit=True)
            del_form.user = request.user
            del_form.save()
        user_cart = CartForAuthenticatedUser(request)
        cart_info = user_cart.get_cart_info()
        cart_products = cart_info['products']
        line_items = [{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': cart_product.product.title,
                    'description': cart_product.product.description
                },
                'unit_amount': int(cart_product.product.get_discount_price() * 100)
            },
            'quantity': cart_product.quantity
        } for cart_product in cart_products]

        STRIPE_SECRET_KEY = ''

        stripe.api_key = STRIPE_SECRET_KEY
        session = stripe.checkout.Session.create(
            line_items=line_items,
            mode='payment',
            success_url=request.build_absolute_uri(reverse('success')),
            cancel_url=request.build_absolute_uri(reverse('checkout')),
        )
        return redirect(session.url, 303)


def success_payment(request):
    user_cart = CartForAuthenticatedUser(request)
    cart_info = user_cart.get_cart_info()
    cart_products = cart_info['products']

    with transaction.atomic():
        order = Order.objects.create(
            user=request.user
        )

        for cart_product in cart_products:
            OrderItem.objects.create(
                order=order,
                product=cart_product.product,
                quantity=cart_product.quantity,
                unit_price=cart_product.product.get_discount_price()
            )
    user_cart.clear()
    return render(request, 'clothes/shopping-cart.html')
