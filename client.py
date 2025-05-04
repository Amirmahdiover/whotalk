import requests
url = "http://127.0.0.1:8000/api/messages/?msg_sender=ali&msg_sender_number=123"
headers = {
    "Authorization": "Bearer 3405feec20a0a1bde5d10625e93d3f358ad7872b:1:aca3bc6c93fcea6d",
}
response = requests.get(url, headers=headers)
print(response.json())
