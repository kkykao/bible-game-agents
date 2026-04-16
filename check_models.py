"""Check available Anthropic models for your API key"""
import os
import sys
from pathlib import Path
from anthropic import Anthropic

# Try to load from .env file
current_dir = Path(__file__).parent
env_file = current_dir / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    print("Error: ANTHROPIC_API_KEY environment variable not set")
    print("Set it with: $env:ANTHROPIC_API_KEY='your-key'")
    sys.exit(1)

client = Anthropic(api_key=api_key)

# Models to test (newest to oldest)
models = [
    # Claude 3.5 models
    "claude-3-5-haiku-20241022",
    "claude-3-5-haiku-latest",
    "claude-3-5-sonnet-20241022",
    "claude-3-5-sonnet-latest",
    "claude-3-5-sonnet-20240620",
    # Claude 3 models
    "claude-3-haiku-20240307",
    "claude-3-sonnet-20240229",
    "claude-3-opus-20240229",
    # Legacy models (if API key is older)
    "claude-2.1",
    "claude-2.0",
    "claude-instant-1.2",
]

print("Testing model access...\n")
for model in models:
    try:
        response = client.messages.create(
            model=model,
            max_tokens=10,
            messages=[{"role": "user", "content": "Say 'OK'"}]
        )
        print(f"✅ {model} - ACCESSIBLE")
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg or "not_found" in error_msg:
            print(f"❌ {model} - NOT AVAILABLE (404)")
        elif "401" in error_msg or "authentication" in error_msg:
            print(f"🔒 {model} - AUTH ERROR")
        else:
            print(f"⚠️  {model} - ERROR: {error_msg[:50]}")

print("\n" + "="*50)
print("RECOMMENDATION: Use the model marked with ✅")
