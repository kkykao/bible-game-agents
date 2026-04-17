import requests

response = requests.post(
    'http://localhost:8000/api/dialogue',
    json={
        'player_name': 'Test User',
        'character_id': 'moses',
        'message': 'What is the significance of the Ten Commandments?'
    },
    timeout=60
)

print('Status Code:', response.status_code)
if response.status_code == 200:
    data = response.json()
    resp_text = data['response']
    print('\nFull Response:')
    print(resp_text[:2000])  # Print first 2000 chars
    print('\n--- Analysis ---')
    print(f'Total length: {len(resp_text)} chars')
    para_count = resp_text.count('[PARA]')
    nl_pair_count = resp_text.count('\n\n')
    print(f'[PARA] markers: {para_count}')
    print(f'Double newlines (paragraph breaks): {nl_pair_count}')
    
    # Check for actual newlines
    print(f'\nFirst 500 chars with visible breaks:')
    print(repr(resp_text[:500]))
else:
    print('Error:', response.text[:500])
