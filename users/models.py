#Imports
from django.db import models  #Import Django models 
from django.contrib.auth.models import User #Import Django User model
from recipes.models import Recipe #Import Recipe model from recipes app

#Profile model extends functionality of an object of Django's User model by adding additional attributes (meaasuring_system_preferences, is_admin, favourite, tobake)
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) #Establishes a one-to-one relationship with Django's built-in User model. Each profile is linked to a unique User object

    measuring_system_choices = [(0, 'Metric'), (1, 'Imperial'),] #Defines user's measuring system choices. User can only choose from a dropdown menu of predefined options

    measuring_system_preference = models.IntegerField(choices = measuring_system_choices, default = 1)#Stores user's measuring system preference

    is_admin = models.BooleanField(default=False) 

    favourite = models.ManyToManyField(Recipe, related_name='favourite_recipes') #Many-to-many relationship with the Recipe model to store the recipes that the user has marked as favourites

    tobake = models.ManyToManyField(Recipe,related_name='tobake_recipes') #Many-to-many relationship with the Recipe model to store the recipes that the user wants to bake

    def __str__(self): #when a Profile object is printed/converted to a string, its username is returned
        return self.user.username

