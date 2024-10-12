from .forms import LoginForm, RegisterForm


def auth_forms(request):
    return {
        'login_form': LoginForm(),
        'register_form': RegisterForm()
    }

