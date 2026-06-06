import requests

response = requests.get("https://openrouter.ai/api/v1/models")
models = response.json().get("data", [])

free_models = [
    m["id"] for m in models 
    if "free" in m["id"].lower() or (m.get("pricing") and m["pricing"].get("prompt") == "0" and m["pricing"].get("completion") == "0")
]

for m in free_models:
    print(m)
