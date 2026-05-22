import requests

url = "https://dummyjson.com/recipes"
response = requests.get(url)

data = response.json()

recipes = data["recipes"]

# 1
print("1. Всі рецепти:")

for recipe in recipes:
    print(recipe["name"])

# 2
italian_count = 0

for recipe in recipes:
    if recipe["cuisine"] == "Italian":
        italian_count += 1

print("\n2. Кількість італійських страв:")
print(italian_count)

# 3
max_recipe = recipes[0]

for recipe in recipes:
    if recipe["caloriesPerServing"] > max_recipe["caloriesPerServing"]:
        max_recipe = recipe

print("\n3. Найбільш калорійна страва:")
print(max_recipe["name"])
print(max_recipe["caloriesPerServing"])

# 4
print("\n4. Страви:")

for recipe in recipes:
    print(recipe["name"])

# 5
total_reviews = 0

for recipe in recipes:
    total_reviews += recipe["reviewCount"]

print("\n5. Загальна кількість переглядів:")
print(total_reviews)