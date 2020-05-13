# limit 15 queries daily
# https://rapidapi.com/ptwebsolution/api/worldwide-restaurants?endpoint=apiendpoint_8bfaa5e8-45b8-42f2-a264-4428a99699df

import requests

url = "https://worldwide-restaurants.p.rapidapi.com/search"

payload = "limit=30&language=en_US&location_id=297704&currency=USD"
headers = {
    'x-rapidapi-host': "worldwide-restaurants.p.rapidapi.com",
    'x-rapidapi-key': "bab91b1a89mshb6facec091e50a8p1e6074jsn39ac62f632ad",
    'content-type': "application/x-www-form-urlencoded"
    }

response = requests.request("POST", url, data=payload, headers=headers)

print(response.text)
