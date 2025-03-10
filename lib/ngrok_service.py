import requests

url = "http://httpbin.org/post"

# Esegui la richiesta POST
response = requests.post(url)

# Estrai solo il contenuto della chiave "data"
hello_world_text = response.json().get("data")

print(hello_world_text)  # Output: Hello World
