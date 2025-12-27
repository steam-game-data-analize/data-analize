import requests
import json

app_id = 1049590  # Eternal Return

url = f"https://store.steampowered.com/appreviewhistogram/{app_id}"
response = requests.get(url, params={'l': 'english'})

print("Status Code:", response.status_code)
print("\nResponse JSON:")
data = response.json()
print(json.dumps(data, indent=2))

print("\n\n=== Checking data structure ===")
if 'rollups' in data:
    print(f"Rollups count: {len(data['rollups'])}")
    if data['rollups']:
        print(f"First rollup type: {type(data['rollups'][0])}")
        print(f"First rollup: {data['rollups'][0]}")

if 'results' in data:
    print(f"\nResults count: {len(data['results'])}")
    if data['results']:
        print(f"First result type: {type(data['results'][0])}")
        print(f"First result: {data['results'][0]}")
