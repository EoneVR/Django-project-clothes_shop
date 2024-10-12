from django import forms
from .models import *
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


class AddToCartForm(forms.Form):
    size = forms.ModelChoiceField(
        queryset=ProductSize.objects.none(),
        widget=forms.HiddenInput(),
    )
    color = forms.ModelChoiceField(
        queryset=ProductColor.objects.none(),
        widget=forms.HiddenInput(),
    )
    quantity = forms.IntegerField(
        widget=forms.TextInput(
            attrs={
                'type': 'text',
                'id': 'quantity',
                'name': 'quantity',
                'class': 'form-control input-number text-center',
                'value': '1'

            }
        )
    )

    def __init__(self, product, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['size'].queryset = ProductSize.objects.filter(product=product)
        self.fields['color'].queryset = ProductColor.objects.filter(product=product)
        self.fields['quantity'].widget.attrs['data-stock'] = product.in_stock


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control'
    }))


class RegisterForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control'
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control'
    }))
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control'
    }))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']


class CommentFormAuthenticated(forms.ModelForm):
    image = forms.ImageField(required=False, widget=forms.FileInput(attrs={
        'class': 'form-control col-lg-6 col-md-4'
    }))
    comment = forms.Field(widget=forms.Textarea(attrs={
        'class': 'form-control col-lg-6 col-md-4'
    }))

    class Meta:
        model = Comment
        fields = ['image', 'comment']


class CommentFormAnonymous(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control  col-lg-6 col-md-4'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control  col-lg-6 col-md-4'
    }))
    image = forms.ImageField(required=False, widget=forms.FileInput(attrs={
        'class': 'form-control  col-lg-6 col-md-4'
    }))
    comment = forms.Field(widget=forms.Textarea(attrs={
        'class': 'form-control col-lg-6 col-md-4'
    }))

    class Meta:
        model = Comment
        fields = ['username', 'email', 'image', 'comment']


class ContactUsForm(forms.ModelForm):
    class Meta:
        model = ContactUs
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Message'
            }),
        }


class DeliveryAddressForm(forms.ModelForm):
    class Meta:
        model = DeliveryAddress
        fields = ['country', 'address', 'city', 'state', 'zipcode', 'phone', 'order_notes']
        widgets = {
            'country': forms.TextInput(attrs={
                'class': 'form-control mt-2 mb-4',
                'placeholder': 'Country / Region *'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control mt-2 mb-4',
                'placeholder': 'Street Address *'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control mt-2 mb-4',
                'placeholder': 'Town / City *'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control mt-2 mb-4',
                'placeholder': 'State *'
            }),
            'zipcode': forms.TextInput(attrs={
                'class': 'form-control mt-2 mb-4',
                'placeholder': 'Zip Code *'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control mt-2 mb-4',
                'placeholder': 'Phone *'
            }),
            'order_notes': forms.TextInput(attrs={
                'class': 'form-control mt-2 mb-4',
                'placeholder': "Notes about your order, e.g. special notes for delivery."
            }),
        }


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'description', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']
        widgets = {
            'avatar': forms.FileInput(attrs={
                'class': 'form-control'
            })
        }


class EditUserForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control'
    }))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']