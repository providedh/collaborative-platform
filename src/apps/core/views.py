from django.shortcuts import render, redirect

from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from django.http import HttpResponse, HttpRequest


# from src.apps.core.forms import SignUpForm


def index(request):  # type: (HttpRequest) -> HttpResponse
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
        # form = SignUpForm(request.POST)
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()

            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)

            return redirect('index')
    else:
        form = UserCreationForm()

    context = {
        'title': 'Home',
        'alerts': None,
        'form': form,
    }

    return render(request, 'core/signup.html', context)


def login(request):  # type: (HttpRequest) -> HttpResponse
    if request.method == 'POST':
        # form = SignUpForm(request.POST)
        form = AuthenticationForm(request.POST)
        if form.is_valid():
            form.save()

            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=raw_password)
            login(request, user)

            return redirect('index')
    else:
        form = AuthenticationForm()

    context = {
        'title': 'Home',
        'alerts': None,
        'form': form,
    }

    return render(request, 'core/login.html', context)
