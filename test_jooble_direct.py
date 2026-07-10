import requests

API_KEY = "16972a27-b0bd-480f-807a-ef3a93639025"
url = f"https://jooble.org/api/{API_KEY}"

headers = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

payload = {"keywords": "technicien"}

response = requests.post(url, json=payload, headers=headers, timeout=10)

print("Status:", response.status_code)
print("Response:", response.text[:1000])