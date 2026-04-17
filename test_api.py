import requests
import json

# Test the dialogue endpoint
response = requests.post(
    'http://localhost:8000/api/dialogue',
    json={
        'player_name': 'Test User',
        'character_id': 'moses',
        'message': 'What is the significance of the Ten Commandments?'
    }
)

print('Status Code:', response.status_code)
if response.status_code == 200:
    data = response.json()
    print('\nResponse text:')
    print(data['response'])
    print('\n--- Checking for [PARA] markers ---')
    if '[PARA]' in data['response']:
        print('✓ Found [PARA] markers in response')
        parts = data['response'].split('[PARA]')
        print(f'✓ Response has {len(parts)} paragraphs')
    else:
        print('✗ No [PARA] markers found')
else:
    print('Error:', response.text[:500])
