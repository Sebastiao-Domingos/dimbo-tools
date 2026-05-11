
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def require_conversion_capability(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            if not request.user.can_convert():
                messages.error(request, 'Atingiu o limite diário de conversões. Faça upgrade para Premium.')
                return redirect('dashboard:index')
        return view_func(request, *args, **kwargs)
    return wrapper