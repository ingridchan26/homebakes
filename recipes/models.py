#Imports
from django.db import models #Import Django models 

#Recipe model defines the attributes of a recipe, each attribute corresponds to a field in the database
class Recipe(models.Model):
    recipe_name = models.CharField(max_length=255)
    intended_serving_size = models.IntegerField() 
    measuring_system_choices = [(0, 'Metric'), (1, 'Imperial'),] #Defines measuring system choices that the recipe can be written in. Recipe measurements can only written in these predefined options
    measuring_system = models.IntegerField(choices = measuring_system_choices, default = 1) #Stores recipe's measuring system 
    slug = models.SlugField(unique=True, blank=True) #Slug for the recipe (used in URLs)
    date_created = models.DateTimeField(auto_now_add=True) 
    image = models.ImageField(default = 'fallback.png', blank=True) 

    def __str__(self): # When a Recipe object is printed/converted to a string, it's name is returned
        return self.recipe_name

#Instruction model defines the attributes of an instruction, each attribute corresponds to a field in the database
class Instruction(models.Model):
    recipe = models.ForeignKey('Recipe',on_delete=models.CASCADE,related_name='instructions') #ForeignKey linking an instruction to a recipe, 1 recipe can have multiple instructions
    step = models.IntegerField() 
    description = models.TextField()
    timer = models.BooleanField(default=False) 
    timer_time = models.FloatField(null=True, blank=True) #If a timer is needed, this field stores the duration (in minutes)

    def __str__(self): #When an Instruction object is printed/converted to a string, it's recipe's name and instruction step are returned
        return f"{self.recipe.recipe_name} - Step {self.step}"

#Ingredient model defines the attributes of an ingredient, each attribute corresponds to a field in the database
class Ingredient(models.Model):
    quantity = models.FloatField() 
    recipe = models.ForeignKey('Recipe',on_delete=models.CASCADE,related_name='ingredients')#ForeignKey linking an ingredient to a recipe, 1 recipe can have multiple ingredients
    uom_choices = [(0, 'cup'), (1, 'tbsp'), (2, 'tsp'), (3, 'oz'), (4, 'lbs'), (5, 'stick'),(6, 'ml'), (7, 'g'),(8,"")] #Set of predefined units of measurement to choose from
    uom = models.IntegerField(choices = uom_choices, default=8) #Unit of measurement for the ingredient 
    instruction = models.ForeignKey('Instruction',on_delete=models.CASCADE,related_name='ingredients')#ForeignKey linking an ingredient to an instruction, 1 instruction can have multiple ingredients
    ing_name = models.CharField(max_length=255)

    def __str__(self):  #When an Ingredient object is printed/converted to a string, 
                        #it's recipe's name and ingredient name are returned
        return f"{self.recipe.recipe_name} - {self.ing_name}"
    
