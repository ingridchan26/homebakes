from django import forms 
from . import models #Import models

#Form for Creating a Recipe
class CreateRecipe(forms.ModelForm):
    class Meta:
        model = models.Recipe 
        fields = ['recipe_name','intended_serving_size','measuring_system',
                    'image'] # These fields will appear in the form for users to fill out





