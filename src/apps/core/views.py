from django.shortcuts import render
from django.http import HttpResponse


def index(request):
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
