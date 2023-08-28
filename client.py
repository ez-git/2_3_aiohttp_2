import requests

url = "http://localhost:8080/ads/1/"
response = requests.get(url)
print(response)

url = "http://localhost:8080/ads/"
json = {"title": 'Title2',
        "description": "Description1",
        "author": 'Author1'}
response = requests.post(url, json=json)
print(response)

url = "http://localhost:8080/ads/1/"
response = requests.get(url)
print(response)

url = "http://localhost:8080/ads/1/"
json = {"title": 'Title2'}
response = requests.patch(url, json=json)
print(response)

#url = "http://localhost:8080/ads/1/"
#response = requests.delete(url)
#print(response)
