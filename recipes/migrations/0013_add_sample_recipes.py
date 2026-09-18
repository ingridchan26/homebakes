from django.db import migrations
from django.utils.text import slugify


RECIPES = [
    {
        "name": "Galaxy Swirl Cupcakes",
        "servings": 12,
        "system": 1,  # imperial
        "ingredients": [
            (1.5, 0, "all-purpose flour"),
            (1, 0, "sugar"),
            (0.5, 0, "cocoa powder"),
            (2, 1, "purple food gel"),
            (2, 1, "blue food gel"),
        ],
        "steps": [
            (1, "Whisk together the flour, sugar, and cocoa powder in a large bowl.", False, None),
            (2, "Split the batter into three bowls and tint each a different galaxy color, then swirl together in cupcake liners.", False, None),
            (3, "Bake until a toothpick comes out clean.", True, 18.0),
        ],
    },
    {
        "name": "Midnight Mocha Brownies",
        "servings": 9,
        "system": 1,
        "ingredients": [
            (1, 5, "unsalted butter"),
            (2, 1, "instant espresso powder"),
            (1, 0, "dark chocolate chips"),
            (1, 0, "sugar"),
        ],
        "steps": [
            (1, "Melt the butter and chocolate chips together until glossy.", False, None),
            (2, "Stir in the espresso powder and sugar until fully combined.", False, None),
            (3, "Bake until the edges are set but the center is still fudgy.", True, 25.0),
        ],
    },
    {
        "name": "Unicorn Rainbow Pancakes",
        "servings": 4,
        "system": 1,
        "ingredients": [
            (2, 0, "pancake mix"),
            (1, 0, "milk"),
            (1, 2, "vanilla extract"),
            (4, 1, "assorted food coloring"),
        ],
        "steps": [
            (1, "Mix pancake batter with milk and vanilla until smooth.", False, None),
            (2, "Divide into small bowls and color each a different rainbow shade.", False, None),
            (3, "Cook each color on a griddle until bubbles form, then flip.", True, 3.0),
        ],
    },
    {
        "name": "Spiced Chai Snickerdoodles",
        "servings": 24,
        "system": 1,
        "ingredients": [
            (2.75, 0, "flour"),
            (1, 0, "sugar"),
            (2, 2, "ground cinnamon"),
            (1, 2, "ground cardamom"),
            (0.5, 2, "ground ginger"),
        ],
        "steps": [
            (1, "Cream the butter and sugar until fluffy, then mix in the spices.", False, None),
            (2, "Roll dough into balls and coat in cinnamon sugar.", False, None),
            (3, "Bake until edges are just golden.", True, 10.0),
        ],
    },
    {
        "name": "Salted Caramel Lava Cookies",
        "servings": 10,
        "system": 1,
        "ingredients": [
            (2, 0, "flour"),
            (10, 3, "soft caramel candies"),
            (1, 2, "flaky sea salt"),
            (1, 5, "butter"),
        ],
        "steps": [
            (1, "Prepare a basic cookie dough and chill for 30 minutes.", True, 30.0),
            (2, "Wrap each dough ball around a caramel candy, sealing completely.", False, None),
            (3, "Bake and sprinkle with flaky salt right out of the oven.", True, 12.0),
        ],
    },
    {
        "name": "Matcha White Chocolate Blondies",
        "servings": 9,
        "system": 1,
        "ingredients": [
            (1, 5, "unsalted butter"),
            (1, 0, "brown sugar"),
            (2, 1, "matcha powder"),
            (1, 0, "white chocolate chips"),
        ],
        "steps": [
            (1, "Brown the butter, then whisk in the brown sugar and matcha.", False, None),
            (2, "Fold in the white chocolate chips and spread into a lined pan.", False, None),
            (3, "Bake until the top is set but the center still looks slightly underdone.", True, 22.0),
        ],
    },
    {
        "name": "Cloud Nine Meringues",
        "servings": 20,
        "system": 1,
        "ingredients": [
            (4, 8, "egg whites"),
            (1, 0, "sugar"),
            (0.5, 2, "vanilla extract"),
            (0.25, 2, "cream of tartar"),
        ],
        "steps": [
            (1, "Whip egg whites with cream of tartar until foamy.", False, None),
            (2, "Gradually add sugar, whipping until stiff glossy peaks form.", False, None),
            (3, "Pipe into clouds and bake low and slow until crisp and dry.", True, 90.0),
        ],
    },
    {
        "name": "Firecracker Cornbread Muffins",
        "servings": 12,
        "system": 1,
        "ingredients": [
            (1, 0, "cornmeal"),
            (1, 0, "flour"),
            (2, 1, "diced jalapeno"),
            (0.5, 0, "shredded cheddar"),
        ],
        "steps": [
            (1, "Whisk the dry ingredients, then fold in jalapeno and cheddar.", False, None),
            (2, "Spoon batter into a muffin tin.", False, None),
            (3, "Bake until golden and a toothpick comes out clean.", True, 20.0),
        ],
    },
    {
        "name": "Honey Lavender Shortbread",
        "servings": 16,
        "system": 1,
        "ingredients": [
            (1, 5, "unsalted butter"),
            (0.5, 0, "powdered sugar"),
            (2, 1, "honey"),
            (1, 2, "dried culinary lavender"),
        ],
        "steps": [
            (1, "Cream butter, powdered sugar, and honey until smooth, then mix in lavender.", False, None),
            (2, "Press dough into a pan and prick all over with a fork.", False, None),
            (3, "Bake low and slow until pale gold, then slice while warm.", True, 35.0),
        ],
    },
    {
        "name": "Cosmic Brownie Batter Dip",
        "servings": 8,
        "system": 1,
        "ingredients": [
            (8, 3, "cream cheese"),
            (0.5, 0, "cocoa powder"),
            (0.5, 0, "brown sugar"),
            (1, 0, "mini chocolate chips"),
        ],
        "steps": [
            (1, "Beat the cream cheese until smooth.", False, None),
            (2, "Mix in cocoa powder and brown sugar until fully combined.", False, None),
            (3, "Fold in mini chocolate chips and chill before serving.", True, 30.0),
        ],
    },
]


def add_recipes(apps, schema_editor):
    Recipe = apps.get_model("recipes", "Recipe")
    Instruction = apps.get_model("recipes", "Instruction")
    Ingredient = apps.get_model("recipes", "Ingredient")

    for data in RECIPES:
        slug = slugify(data["name"])
        if Recipe.objects.filter(slug=slug).exists():
            continue  # Skip if this sample recipe already exists (safe to re-run)

        recipe = Recipe.objects.create(
            recipe_name=data["name"],
            intended_serving_size=data["servings"],
            measuring_system=data["system"],
            slug=slug,
        )

        instructions_by_step = {}
        for step, description, timer, timer_time in data["steps"]:
            instructions_by_step[step] = Instruction.objects.create(
                recipe=recipe,
                step=step,
                description=description,
                timer=timer,
                timer_time=timer_time,
            )

        first_instruction = instructions_by_step[1]
        for quantity, uom, ing_name in data["ingredients"]:
            Ingredient.objects.create(
                quantity=quantity,
                recipe=recipe,
                uom=uom,
                instruction=first_instruction,
                ing_name=ing_name,
            )


def remove_recipes(apps, schema_editor):
    Recipe = apps.get_model("recipes", "Recipe")
    slugs = [slugify(data["name"]) for data in RECIPES]
    Recipe.objects.filter(slug__in=slugs).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("recipes", "0012_alter_instruction_timer_time"),
    ]

    operations = [
        migrations.RunPython(add_recipes, remove_recipes),
    ]
