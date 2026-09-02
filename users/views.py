from django.shortcuts import render, redirect  #Used to render templates and redirect users
from django.contrib.auth.forms import AuthenticationForm #Import Django's Authentification form used for login
from django.contrib.auth import login,logout #Import Django's login/logout function
from .models import Profile #Import Profile class from models.py file
from django.contrib.auth.decorators import login_required #Decorator to restrict access to certain views
from .utils import send_password_reset_email  #Import function defined in utils.py
from .forms import changeMeasuringSystem, UserRegistrationForm #Import forms defined in forms.py file
from recipes.decorators import admin_required #Import decorator defined in decorators.py in recipes folder

# View for customer registration (non-admin users)
def register_view(request):
    if request.method == "POST": #Checks if the form is submitted from the register.html file
        form = UserRegistrationForm(request.POST) #Create a form instance with POST data
        if form.is_valid(): #Check if the data entered is valid
            user = form.save()
            Profile.objects.create(user=user, is_admin=False) #Uses the newly created user to create a profile for them (not an admin)
            login(request, user) #Log them in automatically
            return redirect("recipes:list") #Bring user to the recipe list page
    else:
        form = UserRegistrationForm() #Show an empty form if user hasn't submitted anything
    return render(request, "users/register.html",{ "form": form })

@admin_required #Restricted access to only admin users
def admin_register(request):
    if request.method == "POST": #Checks if the form is submitted from the adminregister.html file
        form = UserRegistrationForm(request.POST)#Create a form instance with POST data
        if form.is_valid():#Check if the data entered is valid
            user = form.save()
            Profile.objects.create(user=user, is_admin=True)#Uses the newly created user to create a profile for them (is an admin)
            return redirect("recipes:list")  #Bring user to the recipe list page
    else:
        form = UserRegistrationForm()#Show an empty form if user hasn't submitted anything
    return render(request, "users/adminregister.html",{ "form": form })

#Displays login form
def login_view(request): 
    if request.method == "POST": #Check if form has been submitted from the login.html
        form = AuthenticationForm(data=request.POST) #Create a form instance with POST data
        if form.is_valid(): 
            user = form.get_user() 
            login(request, user) 
            if user.profile.is_admin:  #Conditional to redirect based on user type
                return redirect("recipes:admin-panel")
            else:
                return redirect("recipes:list")
    else:
        form = AuthenticationForm() 
    return render(request, "users/login.html", {"form": form})

#Allows user to request a link to reset their password
def request_password_reset(request):
    if request.method == "POST": 
        email = request.POST.get("email") 
        user = Profile.objects.filter(user__email=email).first() #Finds user with the given email exists
        if user: #checks if user exists
            reset_link = "http://localhost:8000/users/change-password/" 
            send_password_reset_email(email, reset_link) #calls function defined in utils.py
            return redirect("http://127.0.0.1:8000/") 
        else:  #Show an error message if the email is not found
            return render(request, "users/request_password_reset.html", {"error": "User does not exist"})
    return render(request, "users/request_password_reset.html")

#Function to change password
def change_password(request): 
    messages = ""
    if request.method == 'POST': 
        email = request.POST.get('email') 
        first_entry = request.POST.get('first_entry')  #First password entry 
        new_password = request.POST.get('new_password') #Second password entry
        try:
            profile = Profile.objects.get(user__email=email) 
            user = profile.user 
            #Double entry verification
            if first_entry==new_password: 
                user.set_password(new_password) 
                user.save()
                messages = 'Password successfully updated!'
                return redirect('users:login') 
            else: messages=  'Passwords not the same' #Error message for mismatched passwords
        except Profile.DoesNotExist: #If email doesn't match any user profile, display this error message
            messages = (request, 'User not found.')
    return render(request, 'users/changepassword.html',{'messages':messages})

@login_required #Function is only visible to logged-in users
def logout_view(request):
    if request.method == "POST": #Check if form has been submitted
        logout(request)
        return redirect("recipes:list")

@login_required #Function is only visible to logged-in users
def favouriteslist(request):
    profile = Profile.objects.get(user=request.user) #Get the profile associated with the logged-in user
    favourite_recipes = profile.favourite.all() #Retrieve all favourite recipes linked to the profile
    return render(request, 'users/favourites.html', {'favourite_recipes': favourite_recipes})

@login_required #Function is only visible to logged-in users
def tobakelist(request):
    profile = Profile.objects.get(user=request.user) #Get the logged-in user's profile
    tobake_recipes = profile.tobake.all() #Retrieve all to-bake recipes linked to the profile
    return render(request, 'users/tobake.html', {'tobake_recipes': tobake_recipes})

@login_required #Function is only visible to logged-in users
def change_settings(request):
    profile = Profile.objects.get(user=request.user) #Get the logged-in user's profile
    
    if request.method == 'POST': #Check if form has been submitted through changesettings.html
        form = changeMeasuringSystem(request.POST, instance=profile)  #Use the data fromt the form to update the existing profile instead of creating a new one
        if form.is_valid():
            form.save()
            return redirect('users:change_settings')  #Redirect back to the settings page after saving
    else:
        form = changeMeasuringSystem(instance=profile) #Initialize form with existing profile data
    
    return render(request, 'users/changesettings.html', {'form': form})