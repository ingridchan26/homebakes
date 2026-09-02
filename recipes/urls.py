from django.urls import path
from . import views

app_name = 'recipes'

# URL paths to the different pages
urlpatterns = [
    path('', views.recipes_list, name="list"),
    path('new-recipe/', views.recipe_new, name="new-recipe"),
    path('<slug:slug>', views.recipe_page, name="page"),
    path('<slug:slug>/bakenow/step<int:step>', views.bakenow, name='bakenow'),
    path('admin-panel/',views.admin_panel, name="admin-panel"),
    path('admin-panel/manage-recipes',views.manage_recipes_list,name="manage-recipes-list"),
    path('admin-panel/manage-recipes/<slug:slug>/', views.manage_recipes_list, name='delete-recipe'), 
    path('<slug:slug>/favourite', views.favourite, name='favourite'),
    path('<slug:slug>/tobake', views.tobake, name='tobake'),
    path('admin-panel/edit-recipe/<slug:slug>',views.edit_recipe,name="edit-recipe"),

]

