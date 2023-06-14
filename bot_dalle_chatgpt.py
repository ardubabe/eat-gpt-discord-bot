import requests
import time
import os
from PIL import Image
import discord
import openai

# Discord bot setup
client = discord.Client(intents=discord.Intents.default())

# OpenAI API setup
openai.api_key = os.environ.get("OPENAI_API_KEY")
openai.api_base = os.environ.get("OPENAI_API_BASE")
openai.api_version = "2022-08-03-preview"

# DALL-E image generation function
def generate_dalle_image(caption):
    url = f"{openai.api_base}dalle/text-to-image?api-version={openai.api_version}"
    headers = {"api-key": openai.api_key, "Content-Type": "application/json"}
    body = {
        "caption": caption,
        "resolution": "1024x1024"
    }
    submission = requests.post(url, headers=headers, json=body)
    operation_location = submission.headers['Operation-Location']
    retry_after = submission.headers['Retry-after']
    status = ""
    while status != "Succeeded":
        time.sleep(int(retry_after))
        response = requests.get(operation_location, headers=headers)
        status = response.json()['status']
    image_url = response.json()['result']['contentUrl']
    return image_url

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.mention_everyone:
        return

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
            recipe = response.choices[0].message.content
            recipe_lines = recipe.split('\n')
            dish_name = recipe_lines[0]

            await message.channel.send(recipe)
            image_url = generate_dalle_image(dish_name)
            await message.channel.send(image_url)

client.run(os.environ.get("DISCORD_TOKEN"))
