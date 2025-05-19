from django.http import JsonResponse
from .models import *

def hello(request):
    return JsonResponse({
            "status": "OK",
            "hello": "World",
        }, safe=False)