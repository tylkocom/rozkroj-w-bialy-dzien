import requests
import json

for i in range(1, 3):
    with open(f'tests/input/inp{i}.json') as f:
        data = json.load(f)

    url = 'http://localhost:8001/api/nestings/'
    response = requests.post(url, json={'product': data})
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f'Error: {response.content}')
    with open(f'tests/out{i}.zip', 'wb') as f:
        f.write(response.content)