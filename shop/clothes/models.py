from django.db import models
from colorfield.fields import ColorField
from django.contrib.auth.models import User

# Create your models here.
from django.urls import reverse


class Category(models.Model):
    title = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.title


class Tag(models.Model):
    title = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.title


class Brand(models.Model):
    title = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.title


class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(blank=True, null=True)
    short_description = models.TextField(default='Short description')
    description = models.TextField(default='Main Description')
    information = models.TextField(default='Additional info')
    price = models.DecimalField(max_digits=6, decimal_places=2)
    discount = models.IntegerField(verbose_name='Percent of discount')
    available = models.BooleanField(default=True)
    in_stock = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    sku = models.CharField(max_length=255, blank=True, null=True)
    sales = models.IntegerField(default=0)

    def get_discount_price(self):
        discount_price = float(self.price) - float(self.price) * self.discount / 100
        return discount_price

    def get_first_image(self):
        if len(self.images.all()) > 0:
            return self.images.first().image.url
        else:
            return 'https://pubshamrock.com/wp-content/uploads/2023/04/skoro-zdes-budet-foto.jpg'

    def __str__(self):
        return self.title


class Color(models.Model):
    title = models.CharField(max_length=255)
    color = ColorField(default='#FF0000')

    def __str__(self):
        return self.title


class Size(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.title


class ProductColor(models.Model):
    product = models.ForeignKey(Product, related_name='colors', on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)


class ProductSize(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sizes')
    size = models.ForeignKey(Size, on_delete=models.CASCADE)


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images', blank=True, null=True)


class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comment')
    username = models.CharField(max_length=255)
    email = models.EmailField()
    comment = models.TextField()
    image = models.ImageField(blank=True, null=True, upload_to='comments')
    date = models.DateField(blank=True, null=True, auto_now_add=True)


class WishList(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class ContactUs(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def get_cart_total_quantity(self):
        cart_products = self.cartproduct_set.all()
        total_quantity = sum([product.quantity for product in cart_products])
        return total_quantity

    @property
    def get_cart_total_price(self):
        cart_products = self.cartproduct_set.all()
        total_price = sum([product.get_total_price for product in cart_products])
        return total_price


class CartProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    color = models.CharField(default='No', max_length=255, blank=True, null=True)
    size = models.CharField(default='No', max_length=255, null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)
    quantity = models.IntegerField(default=0)

    @property
    def get_total_price(self):
        total_price = (float(self.product.price) - float(self.product.price) * self.product.discount / 100) * self.quantity
        return total_price


class DeliveryAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    country = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    zipcode = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    order_notes = models.CharField(max_length=255)


class Order(models.Model):
    placed_at = models.DateTimeField(auto_now_add=True, verbose_name='Time of registration')
    user = models.ForeignKey(User, on_delete=models.PROTECT)

    def total_cost(self):
        return sum(item.total_price() for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, verbose_name='Order',
                              related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='Product')
    quantity = models.PositiveIntegerField(verbose_name='Amount of product')
    unit_price = models.DecimalField(max_digits=6, decimal_places=2,
                                     verbose_name='Cost per piece')

    def total_price(self):
        return self.quantity * self.unit_price


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def get_avatar(self):
        if self.avatar:
            return self.avatar.url
        else:
            return 'https://bootdey.com/img/Content/avatar/avatar7.png'

    def get_absolute_url(self):
        return reverse('profile', kwargs={'pk': self.user.pk})

    def get_order_history(self):
        # Fetch all orders associated with this user
        return Order.objects.filter(user=self.user).order_by('-placed_at')


class Article(models.Model):
    title = models.CharField(max_length=255, verbose_name='Title of article')
    description = models.TextField(default='Description', verbose_name='Description')
    image = models.ImageField(upload_to='images/', blank=True, null=True, verbose_name='Image')
    publish_date = models.DateTimeField(auto_now_add=True, verbose_name='Date of publish')
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    def get_image(self):
        if self.image:
            return self.image.url
        else:
            return 'https://pubshamrock.com/wp-content/uploads/2023/04/skoro-zdes-budet-foto.jpg'

    def get_absolute_url(self):
        return reverse('detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title