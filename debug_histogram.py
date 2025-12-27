import requests
import json

def test_histogram_api(app_id, game_name):
    url = f"https://store.steampowered.com/appreviewhistogram/{app_id}"
    response = requests.get(url, params={'l': 'english'})
    
    print(f"\n{'='*80}")
    print(f"{game_name} (App ID: {app_id})")
    print(f"{'='*80}")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data.get('success')}")
        
        if 'rollups' in data:
            rollups = data.get('rollups', [])
            print(f"\nRollups (월별 데이터): {len(rollups)}개")
            if rollups:
                print(f"  - Type: {type(rollups[0])}")
                if isinstance(rollups[0], dict):
                    print(f"  - Sample: {rollups[0]}")
                else:
                    print(f"  - Sample (string): {rollups[0]}")
        
        if 'results' in data:
            results = data.get('results', {})
            print(f"\nResults (일별 데이터):")
            print(f"  - Type: {type(results)}")
            if isinstance(results, dict):
                print(f"  - Keys: {list(results.keys())}")
                if 'rollups' in results:
                    rollups_data = results['rollups']
                    print(f"  - Rollups type: {type(rollups_data)}")
                    print(f"  - Rollups length: {len(rollups_data)}")
                    if rollups_data:
                        print(f"  - First rollup: {rollups_data[0]}")
                        print(f"  - Last rollup: {rollups_data[-1]}")

games = [
    (1049590, "Eternal Return"),
    (730, "Counter-Strike 2"),
]

for app_id, game_name in games:
    test_histogram_api(app_id, game_name)
