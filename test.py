import requests
API_KEY = ''
response = requests.post(
    'https://openrouter.ai/api/v1/chat/completions',
    headers={'Authorization': f'Bearer {API_KEY}'},
    json={"model": "deepseek/deepseek-chat:free", "messages": [{"role": "user", "content": "Hello!"}]}
)
print(response.json())
