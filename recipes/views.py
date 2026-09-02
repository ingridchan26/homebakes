from django.shortcuts import render, redirect
from .models import Recipe, Instruction, Ingredient
from . import forms
from .decorators import admin_required
from django.utils.text import slugify
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from users.models import Profile
from django.urls import reverse
from .forms import CreateRecipe
from django.forms import inlineformset_factory

#Displays a list of all recipes
def recipes_list(request):
    query = request.GET.get('q')  #Retrieve user query
    all_recipes = Recipe.objects.all() 
    recipes = [] 

    if query: #Check is user has requested a query
        # Linear search implementation
        for recipe in all_recipes:
            if query.lower() in recipe.recipe_name.lower(): #Check if user query exists in recipe name
                recipes.append(recipe)
    else:
        recipes = list(all_recipes)

    # Bubble sort by date_created
    n = len(recipes) 
    for i in range(n): 
        for j in range(0, n-i-1):
            if recipes[j].date_created < recipes[j+1].date_created:
                recipes[j], recipes[j+1] = recipes[j+1], recipes[j]

    return render(request, 'recipes/recipes_list.html', {'recipes': recipes})

def uom_conversion(quantity, uom, target_system, ingredient_name,orig_system):
    #Dictionary to store conversion factor to convert imperial to metric and vice versa (multiply for conversion to metric system and divide for conversion to imperial)
    conversion_factors = {
        '0': 240,  # 1 cup is 240ml
        '3': 30,   # 1 ounce is 30g
        '5': 115,   # 1 stick (of butter) is 115 g

        # Specific ingredient conversions (Imperial to Metric)
        'flour': 120,  # 1 cup of flour is 120g
        'sugar': 200,  # 1 cup of sugar is 200g
    }

    #Dictionary to map numerical unit of measurement code to its actual name
    uom_names = {0: 'cup', 1: 'tbsp', 2: 'tsp', 3: 'oz', 4: 'lbs', 5: 'stick', 6: 'ml', 7: 'g', 8: ''}

    # Initialising the variables used to store adjusted measurements
    converted_quantity = quantity
    new_uom = uom

    if orig_system!=target_system:
        if target_system == 0: #if units need to be converted to metric
            if uom == 0: #converting all the cups
                #flour and sugar have different conversions from cups to grams
                if 'flour' in ingredient_name.lower(): 
                    converted_quantity = round(quantity * conversion_factors['flour'],2)
                    new_uom = 'g'
                elif 'sugar' in ingredient_name.lower():
                    converted_quantity = round(quantity * conversion_factors['sugar'],2)
                    new_uom='g'
                else: #converted to ml because if the ingredient is not flour or sugar, it would be a wet ingredient (which uses ml)
                    converted_quantity= round(quantity * conversion_factors['0'],2)
                    new_uom = 'ml'
            elif str(uom) in conversion_factors: #Convert the rest of the imperial measurements to their metric counterpart
                converted_quantity = round(quantity * conversion_factors[str(uom)],2)
                new_uom='g'
        
        elif target_system == 1: #Converted to imperial
            #flour, butter and sugar have different conversions
            if 'flour' in ingredient_name.lower():
                converted_quantity = round(quantity / conversion_factors['flour'],2)
                new_uom = 'cups'
            elif 'butter' in ingredient_name.lower():
                converted_quantity = round(quantity / conversion_factors['5'],2)
                new_uom='stick'
            elif 'sugar' in ingredient_name.lower():
                converted_quantity = round(quantity / conversion_factors['sugar'],2)
                new_uom='cups'
            elif uom == 6:
                converted_quantity = round(quantity / conversion_factors['0'],2)
                new_uom = 'cups'
            elif uom ==  7:
                converted_quantity = round(quantity / conversion_factors['3'],2)
                new_uom = 'oz'
        
        #tbsp and tsp and ingredients with no unit don't need to be converted, but they still need to be represented using their names rather than numerical code
        if uom in [1, 2, 8]:
            new_uom = uom_names[uom]
    
    # if the orig_system = target system, no conversions need to be made but units must still be  represented by its name instead of numerical code
    else:        
        new_uom = uom_names[uom]

    return converted_quantity, new_uom

def recipe_page(request,slug):
    #Retrieve all necessary data from databases
    recipe = Recipe.objects.get(slug=slug) 
    ingredients = recipe.ingredients.all()
    instructions = recipe.instructions.all().order_by('step')
    profile = Profile.objects.get(user=request.user) 
    favourite_recipes = profile.favourite.all()
    tobake_recipes = profile.tobake.all()
    uom_display = profile.measuring_system_preference 
    orig_uom = recipe.measuring_system 

    adjusted_ingredients = [] #Initialise to store adjusted ingredient quantities

    serving_size = recipe.intended_serving_size 
    if request.method=='POST': #Check if user has requested to change serving size
        serving_size = int(request.POST.get('serving_size', recipe.intended_serving_size))
        request.session['serving_size'] = serving_size #Store in session so serving size can be retrieved in the bakenow page without redefining it in every page

        adjusted_ingredients = []
        for ingredient in ingredients:
            adjusted_quantity = round(((ingredient.quantity/recipe.intended_serving_size) * serving_size),1)  #Calculate new ingredient quantity according to the new serving size
            converted_quantity, converted_uom = uom_conversion(adjusted_quantity, ingredient.uom, uom_display, ingredient.ing_name,orig_uom) #Convert the ingredient's unit of measurement if needed using previously defined uom_conversion function
            adjusted_ingredients.append({
                'quantity': converted_quantity,
                'uom': converted_uom,
                'name': ingredient.ing_name
            })   #Store the adjusted ingredient details

    else:    #If no serving size change, convert ingredients using the default serving size
        for ingredient in ingredients:
            converted_quantity, converted_uom = uom_conversion(ingredient.quantity, ingredient.uom, uom_display, ingredient.ing_name,orig_uom)
            adjusted_ingredients.append({
                'quantity': converted_quantity,
                'uom': converted_uom,
                'name': ingredient.ing_name
            })
    request.session['converted_adjusted_ingredients'] = serving_size  # Store in session


    return render(request, 'recipes/recipe_page.html', {'recipe': recipe,
                                                        'ingredients': adjusted_ingredients,
                                                        'instructions': instructions,
                                                        'favourite_recipes': favourite_recipes,
                                                        'tobake_recipes': tobake_recipes,
                                                        'serving_size': serving_size
                                                        })

def bakenow(request,slug,step): #Displays the step-by-step baking instructions for a recipe.
    #Retrieve all necessary data from databases
    recipe = Recipe.objects.get(slug=slug)
    instructions = recipe.instructions.all()
    profile = Profile.objects.get(user=request.user)
    uom_display = profile.measuring_system_preference
    orig_uom = recipe.measuring_system # Original unit of measurement used in the recipe

    #Serving size set by user can be retrieved for calculation without the user entering it again
    serving_size = request.session.get('serving_size', recipe.intended_serving_size)

    #Ensure the step number is within valid bounds
    if step < 0:
        step = 0 
    elif step >= instructions.count():
        step = instructions.count() - 1 

    #Get instructions/ingredients for this step specifically
    current_instruction = instructions.get(step=step+1) 
    related_ingredients = current_instruction.ingredients.all() 

    #Adjust ingredient quantities based on the selected serving size and unit of measurement
    adjusted_ingredients = []
    for ingredient in related_ingredients:
        adjusted_quantity = round(((ingredient.quantity/recipe.intended_serving_size) * serving_size),1)
        converted_quantity, converted_uom = uom_conversion(adjusted_quantity, ingredient.uom, uom_display, ingredient.ing_name, orig_uom)
        adjusted_ingredients.append({
            'quantity': converted_quantity,
            'uom': converted_uom,
            'name': ingredient.ing_name
        })

    #Set the timer if the current step requires one
    if current_instruction.timer == True:
        timer_time_seconds = current_instruction.timer_time * 60  #Convert minutes to seconds
    else:
        timer_time_seconds=0 

    materials = {
        'recipe': recipe,
        'current_instruction': current_instruction,
        'related_ingredients': adjusted_ingredients,
        'step': step,
        'total_steps': instructions.count(),
        'timer_time_seconds': timer_time_seconds,
    }
    return render(request,'recipes/bakenow.html', materials)

def favourite(request,slug): #Adds/removes recipes to/from "Favourites" collection
    user = request.user 
    recipe = Recipe.objects.get(slug=slug)  
    profile = Profile.objects.get(user=user) 
    
    #Check if the recipe is already in the user's favourite list
    if profile.favourite.filter(slug=slug).exists():
        profile.favourite.remove(recipe)  #Remove from favourites if already present
    else:
        profile.favourite.add(recipe) #Add to favourites if not present
    return HttpResponseRedirect(reverse('recipes:page',args=[slug]))

def tobake(request,slug):#Adds/removes recipes to/from "To bake" collection
    user = request.user 
    recipe = Recipe.objects.get(slug=slug)
    profile = Profile.objects.get(user=user) 
    
    #Check if the recipe is already in the user's To bake list
    if profile.tobake.filter(slug=slug).exists():
        profile.tobake.remove(recipe) #Remove from favourites if already present
    else:
        profile.tobake.add(recipe) #Add to favourites if not present
    return HttpResponseRedirect(reverse('recipes:page',args=[slug]))

# All following functions restrict access to admin users only
@admin_required
def manage_recipes_list(request, slug=None): #Displays a list of all recipes for admins to manage.
    #Delete recipe is requested
    if slug and request.method == "POST": 
        recipe = Recipe.objects.get(slug=slug) 
        recipe.delete()
        return redirect('recipes:manage-recipes-list') 
    all_recipes = Recipe.objects.all() 
    recipes = list(all_recipes) 

    # Bubble sort by date_created
    n = len(recipes) 
    for i in range(n): 
        for j in range(0, n-i-1):
            if recipes[j].date_created < recipes[j+1].date_created:
                recipes[j], recipes[j+1] = recipes[j+1], recipes[j]
    return render(request, 'recipes/manage_recipes.html', {'recipes': recipes})

@admin_required
def admin_panel(request): #Renders the admin panel where admins can go to manage recipes page or create admin page
    return render(request,'recipes/admin_panel.html')

@admin_required
def recipe_new(request):
    if request.method=='POST':
        form = forms.CreateRecipe(request.POST, request.FILES) #Initialize the recipe creation form with submitted data and uploaded files
        #Save form if valid
        if form.is_valid():
            newrecipe = form.save(commit=False)
            newrecipe.slug = slugify(newrecipe.recipe_name) #Fill the slug field to the name of the recipe
            newrecipe.save() 
            return redirect('recipes:list')
    else:
        form = forms.CreateRecipe()
    return render(request,"recipes/recipe_new.html", {'form': form})

@admin_required 
def edit_recipe(request, slug):
    InstructionFormSet = inlineformset_factory(Recipe, Instruction, fields=('step', 'description', 'timer', 'timer_time')) #Create formset for instructions related to a recipe

    IngredientFormSet = inlineformset_factory(Recipe, Ingredient, fields=('ing_name','quantity','uom','instruction')) #Create formset for ingredient related to a recipe

    recipe = Recipe.objects.get(slug=slug) 

    #Initialize forms for the recipe, its related instructions and ingredients with existing data (so current data will be visible to the viewer) 
    recipe_form = CreateRecipe(instance=recipe)
    instruction_formset = InstructionFormSet(instance=recipe)
    ingredient_formset = IngredientFormSet(instance=recipe)

    #When editing the ingredient form to indicate which instruction step the ingredient belongs to, a dropdown menu of only the instructions of the relevant recipe can be selected to avoid accidential selection instructions related to a different recipe
    for form in ingredient_formset:
        form.fields['instruction'].queryset = Instruction.objects.filter(recipe=recipe)

    #Handles form submissions
    if 'save_recipe' in request.POST: 
        recipe_form = CreateRecipe(request.POST, instance=recipe)
        if recipe_form.is_valid():
            recipe_form.save() 
            return redirect('recipes:edit-recipe', slug = slug) 
    if 'save_instructions' in request.POST: 
        instruction_formset = InstructionFormSet(request.POST, instance=recipe)
        if instruction_formset.is_valid():
            instruction_formset.save() 
            return redirect('recipes:edit-recipe', slug=slug)  
    elif 'save_ingredients' in request.POST: 
        ingredient_formset = IngredientFormSet(request.POST, instance=recipe)
        if ingredient_formset.is_valid():
            ingredient_formset.save()  
            return redirect('recipes:edit-recipe', slug=slug)  
    
    context = {'recipe_form': recipe_form,
               'instruction_formset': instruction_formset,
               'ingredient_formset': ingredient_formset,
               'recipe': recipe}
    return render(request, 'recipes/edit_recipe.html', context)