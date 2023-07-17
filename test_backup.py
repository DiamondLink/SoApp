import requests

APP_KEY = '2tn6o03mhzqz3or'
APP_SECRET = 'ejj3dsfgzws8db2'
ACCESS_CODE = '8NZktHP3XAUAAAAAAAAAFWNwZoDNfJWcWnpMFRlSA1g'

url = "https://api.dropboxapi.com/oauth2/token"
headers = {"Content-Type": "application/x-www-form-urlencoded"}
data = {
    "code": ACCESS_CODE,
    "grant_type": "authorization_code"
}
response = requests.post(url, headers=headers, data=data, auth=(APP_KEY, APP_SECRET))

if response.status_code == 200:
    print(response.json())
else:
    print(f"Request failed with status code {response.status_code}")
