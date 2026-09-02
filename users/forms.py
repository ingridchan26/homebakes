from django import forms
from django.contrib.auth.models import User 
from .models import Profile 
from django.contrib.auth.forms import UserCreationForm 

#Custom User Registration Form which extends Django's built-in UserCreationForm
class UserRegistrationForm(UserCreationForm):
    is_admin = forms.BooleanField(required=False) #Add is_admin field to the form
    class Meta:
        model = User 
        fields = ['username', 'email', 'password1','password2', 'is_admin'] #These fields will appear in the sign-up form. 'username', 'email', 'password1','password2' are all from Django's UserCreationForm, but 'is_admin' is from this custom form. 
    
#Form for Changing the Measuring System Preference
class changeMeasuringSystem(forms.ModelForm):
    class Meta:
        model = Profile 
        fields = ['measuring_system_preference']