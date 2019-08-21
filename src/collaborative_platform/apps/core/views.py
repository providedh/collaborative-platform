from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect

from .forms import SignUpForm, LogInForm
from apps.index_and_search.models import User as ESUser


def index(request):  # type: (HttpRequest) -> HttpResponse
    if request.user.is_authenticated:
        return redirect('projects', request.user.pk)
    else:
        alerts = [
            {
                'type': 'success',
                'message': 'Alert test',
            }
        ]

        context = {
            'title': 'Home',
            'alerts': alerts,
        }

        return render(request, 'core/index.html', context)


def signup(request):  # type: (HttpRequest) -> HttpResponse
    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.profile.agree_to_terms = form.cleaned_data.get('agree_to_terms')
            user.save()

            raw_password = form.cleaned_data.get('password1')
            user = auth.authenticate(username=user.username, password=raw_password)
            auth.login(request, user)

            name = "{} {}".format(user.first_name, user.last_name)
            es_user = ESUser(id=user.id, name=name)
            es_user.save()

            return redirect('index')
    else:
        form = SignUpForm()

    context = {
        'title': 'Sign Up',
        'alerts': None,
        'form': form,
    }

    return render(request, 'core/signup.html', context)


def login(request):  # type: (HttpRequest) -> HttpResponse
    if request.method == 'POST':
        form = LogInForm(data=request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password')
            user = auth.authenticate(username=username, password=raw_password)
            auth.login(request, user)

            return redirect('index')
    else:
        form = LogInForm()

    context = {
        'title': 'Log In',
        'alerts': None,
        'form': form,
    }

    return render(request, 'core/login.html', context)


def logout(request):  # type: (HttpRequest) -> HttpResponse
    auth.logout(request)

    alerts = [
        {
            'type': 'success',
            'message': 'You successfully logged out.',
        }
    ]

    context = {
        'title': 'Home',
        'alerts': alerts,
    }

    return render(request, 'core/index.html', context)


@login_required()
def user(request, user_id): # type: (HttpRequest, int) -> HttpResponse
    user = User.objects.get(id=user_id)

    context = {
        'title': '{0} {1} - User details'.format(request.user.first_name, request.user.last_name),
        'alerts': None,
        'user': user
    }

    return render(request, 'core/user.html', context)
