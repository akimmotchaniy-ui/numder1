import requests
from pprint import pprint

url = 'https://dummyjson.com/products'
# url = 'https://www.ukr.net/'
params = {
    'limit': 0,
    'skip': 0
}

response = requests.get(url=url, params=params)
# print(response.content)
# print(response.text)
response_json = response.json()
pprint(response_json)