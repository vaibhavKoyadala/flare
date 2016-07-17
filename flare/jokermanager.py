from django.http.response import HttpResponseRedirect
from models import Flare

def joker_required(on_fail):
    """
    Decorator which calls on_fail()
    if request.joker is None
    """
    def decorator(func):
        def decorated_func(request, *args, **kwargs):
            if request.joker is None:
                return on_fail(request)
            return func(request, *args, **kwargs)
        return decorated_func
    return decorator

def no_joker(on_fail):
    """
    Decorator which calls on_fail()
    if request has a valid joker
    """
    def decorator(func):
        def decorated_func(request, *args, **kwargs):
            if request.joker is not None:
                return on_fail()
            return func(request, *args, **kwargs)
        return decorated_func
    return decorator

def authenticate(name, password):
    try:
        flare = Flare.objects.get(name__iexact=name)
        if flare.password == password:
            return flare
    except :
        pass
    return None

def login_joker(request, joker):
    request.session['joker_id'] = joker.id

def logout_joker(request):
    request.joker.delete()
    del request.session['joker_id']