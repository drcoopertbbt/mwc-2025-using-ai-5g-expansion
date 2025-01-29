import requests
import json
import sys

api_key = "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"
base_url = "https://integrate.api.nvidia.com/v1"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

data = {
    "model": "meta/llama-3.3-70b-instruct",
    "messages": [{"role": "user", "content": "Write a limerick about the wonders of GPU computing."}],
    "temperature": 0.2,
    "top_p": 0.7,
    "max_tokens": 1024,
    "stream": True
}

try:
    print("Sending request to NVIDIA API...")
    response = requests.post(
        f"{base_url}/chat/completions",
        headers=headers,
        json=data,
        stream=True
    )
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        sys.exit(1)

    print("\nResponse from NVIDIA API:")
    for line in response.iter_lines():
        if line:
            line = line.decode('utf-8')
            if line.startswith('data: '):
                try:
                    content = json.loads(line[6:])
                    if content.get('choices') and content['choices'][0].get('delta', {}).get('content'):
                        print(content['choices'][0]['delta']['content'], end='', flush=True)
                except json.JSONDecodeError:
                    continue

except Exception as e:
    print(f"Error: {str(e)}")
    raise
