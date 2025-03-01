import requests
import time
import os

with open("keys.txt") as f:
    # converting our text file to a list of lines
    lines = f.read().split('\n')
    # openai api key
    api_key = lines[1]
    # discord token
    DISCORD_TOKEN = lines[7]
    api_base = lines[9]
# close the file
f.close()


api_version = '2022-08-03-preview'
url = "{}dalle/text-to-image?api-version={}".format(api_base, api_version)
headers= { "api-key": api_key, "Content-Type": "application/json" }
body = {
    "caption": "A dog in a hat",
    "resolution": "1024x1024"
}
submission = requests.post(url, headers=headers, json=body)
operation_location = submission.headers['Operation-Location']
retry_after = submission.headers['Retry-after']
status = ""
while (status != "Succeeded"):
    time.sleep(int(retry_after))
    response = requests.get(operation_location, headers=headers)
    status = response.json()['status']
image_url = response.json()['result']['contentUrl']
print(image_url)
