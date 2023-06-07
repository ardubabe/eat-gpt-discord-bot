import requests
import time
import os
from PIL import Image
import discord
import openai
import logging  

openai.api_type = "azure"
openai.api_version = '2022-08-03-preview'

# create an object that will control our discord bot
client = discord.Client(intents=discord.Intents.default())

with open("keys.txt") as f:
    # converting our text file to a list of lines
    lines = f.read().split('\n')
    # openai api key
    openai.api_key = lines[1]
    # discord token
    DISCORD_TOKEN = lines[7]
    openai.api_base = lines[9]
# close the file
f.close()

@client.event
async def on_ready():
    # print out nice statment saying our bot is online (only in command prompt)
    print(f'{client.user} has connected to Discord!')

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
    elif client.user.mentioned_in(message): 
        url = "{}dalle/text-to-image?api-version={}".format(openai.api_base, openai.api_version)
        headers= { "api-key": openai.api_key, "Content-Type": "application/json" }
        body = {
            "caption": message.content,
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

        response = openai.ChatCompletion.create(
			engine="GPT-4",
			messages=[
			{"role": "system", "content": "I will give you a list of leftover food. Give me a recipe I can make using only the leftovers I have provided and Hellmann's mayonnaise. Provide the dish name, don't title it dish name. Then give me the ingredients list in the format of '- Base, - Fruit and Veg, - Protein and - Magic Touch'. Base is carbohydrates, and magic touch is always Hellmann's Mayonnaise. Then give me the instructions to make the meal in simple terms. Make sure all responses are less than 1500 characters"},
			{"role": "user", "content": message.content}
			]
		)
        await message.channel.send(image_url, response.choices[0].message.content)

client.run(DISCORD_TOKEN)