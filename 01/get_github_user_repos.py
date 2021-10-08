import requests
import json

name = 'Wrexan'
my_params = {
    'q': name
}
export_data = {'repositories': []}
user_name = 'yuwinzer'
url = 'https://api.github.com/users/'+user_name+'/repos'

response = requests.get(url, params=my_params)
if response.ok:
    j_data = response.json()
    for i in range(len(j_data)):
        repo_name = j_data[i].get("name")
        export_data['repositories'].append({
            'name': user_name,
            'repo': repo_name})
        print(repo_name)
else:
    print(response)


with open(user_name+'_repos.json', 'w') as outfile:
    json.dump(export_data, outfile)
