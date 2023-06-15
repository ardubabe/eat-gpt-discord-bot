import requests
import time
import os
from PIL import Image
import discord
import openai
import logging

logging.basicConfig(level=logging.INFO)  
logging.info('Worker script started')  

openai.api_type = "azure"
openai.api_version = "2023-03-15-preview"

# specifying our server
GUILD = "{ardubabe's server}"

# create an object that will control our discord bot
client = discord.Client(intents=discord.Intents.default())

# env variables to be read by Digital Ocean
openai.api_key = os.environ.get("API_KEY")
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
openai.api_base = os.environ.get("API_BASE")

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

# # DALL-E image generation function
# async def generate_dalle_image(caption):
#     # url = f"{openai.api_base}dalle/text-to-image?api-version={openai.api_version}"
#     url = "{}dalle/text-to-image?api-version={}".format(openai.api_base, openai.api_version)
#     headers = {"api-key": openai.api_key, "Content-Type": "application/json"}
#     body = {
#         "caption": caption,
#         #"caption": dish_name,
#         "resolution": "1024x1024"
#     }
#     submission = requests.post(url, headers=headers, json=body)
#     operation_location = submission.headers['Operation-Location']
#     print(submission.headers)
#     retry_after = submission.headers['Retry-after']
#     status = ""
#     while status != "Succeeded":
#         time.sleep(int(retry_after))
#         response = requests.get(operation_location, headers=headers)
#         print(operation_location)
#         status = response.json()['status']
#     image_url = response.json()['result']['contentUrl']
#     return image_url



@client.event
async def on_message(message):
    # this prevents inifinte loops of bot talking to bot
    # if author of the message is the bot, don't do anything    
    if message.author == client.user:
        return
    # ignore @everyone mentions
    if message.mention_everyone:
        return
    # if the message mentions the bot, then do something
    if client.user.mentioned_in(message):
        if any(greeting in message.content.lower() for greeting in ['hi', 'hello', 'hey']):
            response = "Hi, I'm your leftovers bot! Please give me a list of your leftovers, and I will generate a recipe for you. Don't forget to mention me @hogarth-leftovers-bot-demo in the message!"
            await message.channel.send(response)
        else:
            response = openai.ChatCompletion.create(
                engine="GPT-4",
                messages=[
                    {"role": "system", "content": "I will give you a list of leftover food. Give me a recipe I can make using only the leftovers I have provided and Hellmann's mayonnaise. Provide the dish name, don't title it dish name. Then give me the ingredients list in the format of '- Base, - Fruit and Veg, - Protein and - Magic Touch'. Base is carbohydrates, and magic touch is always Hellmann's Mayonnaise. Then give me the instructions to make the meal in simple terms. Make sure all responses are less than 1500 characters"},
                    {"role": "user", "content": message.content}
                ]
            )
            recipe_name = response.choices[0].message.content.split('\n')[0]  # Extract the recipe name

            # Use recipe name as prompt for DALL-E image generation
            url = "{}dalle/text-to-image?api-version={}".format(openai.api_base, openai.api_version)
            headers = {"api-key": os.environ.get("API_KEY"), "Content-Type": "application/json"}
            body = {
                "caption": recipe_name,
                "resolution": "1024x1024"
            }
            submission = requests.post(url, headers=headers, json=body)
            if 'operation-location' not in submission.headers:
                logging.error("Error: 'operation-location' not found in the response headers.")
                logging.error("Response Headers: {}".format(submission.headers))
                await message.channel.send("An error occurred while generating the image. Please try again later.")
                return
            operation_location = submission.headers['Operation-Location']
            retry_after = submission.headers['Retry-after']
            status = ""
            while status != "Succeeded":
                time.sleep(int(retry_after))
                response = requests.get(operation_location, headers=headers)
                status = response.json()['status']
            image_url = response.json()['result']['contentUrl']
            print(image_url)

            await message.channel.send(image_url)

client.run(DISCORD_TOKEN)
