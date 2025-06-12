import requests
API_KEY = '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'
response = requests.post(
    'https://openrouter.ai/api/v1/chat/completions',
    headers={'Authorization': f'Bearer {API_KEY}'},
    json={"model": "deepseek/deepseek-chat:free", "messages": [{"role": "user", "content": "Hello!"}]}
)
print(response.json())