"""
Moderator access decorator.
Allows access to staff (moderators) and superusers.
Usage: @moderator_required
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def moderator_required(view_func):
    """Allow only is_staff or is_superuser users."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, '🚫 Access denied. Moderator privileges required.')
            return redirect('players:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper
