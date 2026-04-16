from anthropic import Anthropic
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('ANTHROPIC_API_KEY')
client = Anthropic(api_key=api_key)

models = ['claude-sonnet', 'claude-haiku', 'claude-opus']

for model in models:
    try:
        response = client.messages.create(
            model=model,
            max_tokens=1,
            messages=[{'role': 'user', 'content': 'hi'}]
        )
        print(f'✅ SUCCESS: {model}')
        break
    except Exception as e:
        error_msg = str(e).lower()
        if '404' in str(e) or 'not_found' in error_msg:
            print(f'❌ NOT FOUND: {model}')
        else:
            print(f'⚠️ ERROR: {model} - {str(e)[:60]}')
