import requests

url = "https://github.com/progit/progit2-ru/releases/download/2.1.123/progit.pdf"

response = requests.get(url)
print(response.status_code)
with open("progit.pdf", "wb") as file:
    file.write(response.content)

print("Файл успішно завантажено!")