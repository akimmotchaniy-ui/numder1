import requests
import json

url = "http://api.open-notify.org/astros.json"

response = requests.get(url)
data = response.json()

with open("astros.json", "w", encoding="utf-8") as file:
    json.dump(data, file, indent=4)

print("Файл успішно створено!")
