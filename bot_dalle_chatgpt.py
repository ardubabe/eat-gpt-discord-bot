import logging
import os
import requests
import time
from PIL import Image
import discord
import openai

logging.basicConfig(level=logging.INFO)
logging.info('Worker script started')

openai.api_type = "azure"
openai.api_version = "2023-03-15-preview"

# specifying our server
GUILD = "{ardubabe's server}"

# create an object that will control our discord bot
client = discord.Client(intents=discord.Intents.default())
# env variables to be read by railway
openai.api_key = os.environ.get("API_KEY")
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
openai.api_base = os.environ.get("API_BASE")

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break
    # print out a nice statement saying our bot is online (only in command prompt)
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user or message.mention_everyone:
        return
    
    if client.user.mentioned_in(message):
        # Generate recipe using OpenAI Chat API
        response = openai.ChatCompletion.create(
            engine="GPT-4",
            messages=[
                {"role": "system", "content": "I will give you a list of leftover food. Give me a recipe I can make using only the leftovers I have provided and Hellmann's mayonnaise. Provide the dish name, don't title it dish name. Then give me the ingredients list in the format of '- Base, - Fruit and Veg, - Protein and - Magic Touch'. Base is carbohydrates, and magic touch is always Hellmann's Mayonnaise. Then give me the instructions to make the meal in simple terms. Make sure all responses are less than 1500 characters"},
                {"role": "user", "content": message.content}
            ]
        )
        recipe = response.choices[0].message.content

        # Extract the dish name from the recipe response
        dish_name = recipe.splitlines()[0]

        # Generate DALL-E image using OpenAI API
        url = "{}dalle/text-to-image?api-version={}".format(openai.api_base, openai.api_version)
        headers = {"api-key": openai.api_key, "Content-Type": "application/json"}
        body = {
            "caption": dish_name,
            "resolution": "1024x1024"
        }
        submission = requests.post(url, headers=headers, json=body)
        if 'Operation-Location' in submission.headers:
            operation_location = submission.headers['Operation-Location']
            retry_after = submission.headers.get('Retry-after', '1')
            status = ""

            # Wait for image generation to complete
            while status != "Succeeded":
                time.sleep(int(retry_after))
                response = requests.get(operation_location, headers=headers)
                status = response.json()['status']
            image_url = response.json()['result']['contentUrl']

            # Send recipe and image URLs as responses to the Discord channel
            await message.channel.send(recipe)
            await message.channel.send(image_url)
        else:
            await message.channel.send("Sorry, an error occurred while generating the DALL-E image.")
            await message.channel.send(recipe)

client.run(DISCORD_TOKEN)
