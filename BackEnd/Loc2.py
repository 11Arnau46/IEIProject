import requests

api_key = '3b3eb29261ae4a61bd9fc55c2e50f74d'
url = "https://api.geoapify.com/v1/geocode/reverse?lat=38.432248&lon=-0.381573&format=json&apiKey=" + api_key

response = requests.get(url)
print(response.json())