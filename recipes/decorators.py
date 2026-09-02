from django.http import HttpResponseForbidden #Imports the response used to deny access to unauthorized users
from functools import wraps # Imports wraps to properly preserve the original function’s metadata when wrapping it

#Custom decorator to restrict access to admin users only
def admin_required(view_func):
    @wraps(view_func) 
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.profile.is_admin: #Check if the user is authenticated and is an admin
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("You are not authorized to view this page.") #If the user is not an admin, return a 403 Forbidden response

    return _wrapped_view 


