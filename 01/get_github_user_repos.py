import requests

name = 'Wrexan'
my_params = {
    'q': name
}

url = "https://api.github.com/users/yuwinzer/repos"

response = requests.get(url, params=my_params)
text = response.text
if response.ok:
    j_data = response.json()
    for i in range(len(j_data)):
        print(j_data[i].get("name"))
else:
    print(response)
