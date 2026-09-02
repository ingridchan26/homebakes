from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name="register"),
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),
    path('favourites/', views.favouriteslist, name='favourites'),
    path('tobake/', views.tobakelist, name='tobakes'),
    path('adminregister/', views.admin_register, name="adminregister"),
    path('password-reset/', views.request_password_reset, name='request_password_reset'),
    path('change-password/', views.change_password, name='change_password'),
    path('settings/',views.change_settings,name='change_settings')




]
