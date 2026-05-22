import requests

url = "https://dummyjson.com/recipes?limit=0"
response = requests.get(url)

data = response.json()
recipes = data["recipes"]

all_recipes = []
italian_count = 0
max_recipe = recipes[0]
total_reviews = 0

for recipe in recipes:

    all_recipes.append(recipe["name"])

    if recipe["cuisine"] == "Italian":
        italian_count += 1

    if recipe["caloriesPerServing"] > max_recipe["caloriesPerServing"]:
        max_recipe = recipe

    total_reviews += recipe["reviewCount"]


print("1. Всі рецепти:")
for name in all_recipes:
    print(name)

print("\n2. Кількість італійських страв:")
print(italian_count)

print("\n3. Найбільш калорійна страва:")
print(max_recipe["name"])
print(max_recipe["caloriesPerServing"])

print("\n4. Страви:")
for name in all_recipes:
    print(name)

print("\n5. Загальна кількість переглядів:")
print(total_reviews)