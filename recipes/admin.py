from django.contrib import admin #Import Django's admin module to manage models in the admin interface (This is something that comes with Django, which is useful for developers to populate databases, the admin interface is not part of this product)
from .models import Recipe, Instruction, Ingredient #Import the models to be registered in the admin interface

#This class customises how the Recipe model appears and behaves in the admin interface
class RecipeAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("recipe_name",)} #Automatically populate the 'slug' field according to the 'recipe_name' field


# Register the models here to make them manageable through the Django admin site
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Instruction)
admin.site.register(Ingredient)

