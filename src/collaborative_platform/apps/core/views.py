import os

from django.contrib import auth, messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AdminPasswordChangeForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect
from social_django.models import UserSocialAuth

from apps.index_and_search.models import User as ESUser
from apps.views_decorators import objects_exists, static_file_exists

from .forms import SignUpForm, LogInForm

from collaborative_platform.settings import STATIC_ROOT


def index(request):  # type: (HttpRequest) -> HttpResponse
    if request.user.is_authenticated:
        context = {
            'title': 'Projects',
            'alerts': None,
        }

        return render(request, 'projects/projects.html', context)
    else:
        context = {
            'title': 'Home',
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

            # name = "{} {}".format(user.first_name, user.last_name)
            # es_user = ESUser(id=user.id, name=name)
            # es_user.save()
            # TODO: possibly enable ES indexing again if needed

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


@objects_exists
def user(request, user_id):  # type: (HttpRequest, int) -> HttpResponse
    user = User.objects.get(id=user_id)

    context = {
        'title': '{0} {1} - User details'.format(user.first_name, user.last_name),
        'alerts': None,
        'user': user,
        'user_url': request.get_raw_uri()
    }

    return render(request, 'core/user.html', context)


@login_required
def settings(request):  # type: (HttpRequest) -> HttpResponse
    user = request.user

    try:
        orcid_login = user.social_auth.get(provider='orcid')
    except UserSocialAuth.DoesNotExist:
        orcid_login = None

    try:
        facebook_login = user.social_auth.get(provider='facebook')
    except UserSocialAuth.DoesNotExist:
        facebook_login = None

    try:
        google_login = user.social_auth.get(provider='google-oauth2')
    except UserSocialAuth.DoesNotExist:
        google_login = None

    can_disconnect = (user.social_auth.count() > 1 or user.has_usable_password())

    context = {
        'title': 'Settings',
        'orcid_login': orcid_login,
        'facebook_login': facebook_login,
        'google_login': google_login,
        'can_disconnect': can_disconnect,
    }

    return render(request, 'core/settings.html', context)


@login_required
def password(request):  # type: (HttpRequest) -> HttpResponse
    if request.user.has_usable_password():
        PasswordForm = PasswordChangeForm
    else:
        PasswordForm = AdminPasswordChangeForm

    if request.method == 'POST':
        form = PasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Your password was successfully updated.')

            return redirect('password')
        else:
            messages.error(request, 'please correct the error below.')

    else:
        form = PasswordForm(request.user)

    context = {
        'form': form
    }

    return render(request, 'core/password.html', context)


@login_required
@static_file_exists
def static_docs(request, file_name):  # type: (HttpRequest, str) -> HttpResponse
    if request.method == 'GET':
        file_path = os.path.join(STATIC_ROOT, 'docs', file_name)

        with open(file_path, 'rb') as file:
            file_content = file.read()

        return HttpResponse(file_content, content_type='application/octet-stream')

def fonts(request):  # type: (HttpRequest) -> HttpResponse
    return render(request, 'static-google-fonts.css', None)
