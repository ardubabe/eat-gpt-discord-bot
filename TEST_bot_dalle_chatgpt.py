import discord
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials

import requests
import time

# create an object that will control our discord bot
client = discord.Client(intents=discord.Intents.default())

# Initialize Azure Text Analytics and Computer Vision clients
text_analytics_key = 'YOUR_TEXT_ANALYTICS_KEY'
text_analytics_endpoint = 'YOUR_TEXT_ANALYTICS_ENDPOINT'
computer_vision_key = 'YOUR_COMPUTER_VISION_KEY'
computer_vision_endpoint = 'YOUR_COMPUTER_VISION_ENDPOINT'

text_analytics_client = TextAnalyticsClient(text_analytics_endpoint, AzureKeyCredential(text_analytics_key))
computer_vision_client = ComputerVisionClient(computer_vision_endpoint, CognitiveServicesCredentials(computer_vision_key))

@client.event
async def on_message(message):
    # Ignore messages sent by the bot itself
    if message.author == client.user:
        return

    # Get the first line of the ChatGPT response as the prompt
    prompt = message.content.split('\n')[0]

    # Generate an image using DALL-E
    image = generate_dalle_image(prompt)

    # Send the generated image back to the user
    await message.channel.send(file=discord.File(image, 'generated_image.png'))

def generate_dalle_image(prompt):
    # Use Azure Text Analytics to detect the language of the prompt
    response = text_analytics_client.detect_language([prompt])[0]
    language = response.primary_language.iso6391_name

    # Check if the language is English, as DALL-E currently supports English prompts only
    if language == 'en':
        # Generate image using DALL-E
        # Add your DALL-E code here

        # Placeholder code to generate a random image URL
        image_url = 'https://via.placeholder.com/500x500'  # Replace with actual DALL-E image URL

        # Download the image
        os.system(f'wget {image_url} -O generated_image.png')

        return 'generated_image.png'
    else:
        return None






@client.event
async def on_message(message):
    # Ignore messages sent by the bot itself
    if message.author == client.user:
        return
    # ignore @everyone mentions
    if message.mention_everyone:
        return
    # if the message mentions the bot, then do something
    elif client.user.mentioned_in(message): 

        # Get the first line of the ChatGPT response as the prompt
        prompt = message.content.split('\n')[0]

        # Generate an image using DALL-E
        ## image = generate_dalle_image(prompt)

        url = "{}dalle/text-to-image?api-version={}".format(api_base, api_version)
        headers= { "api-key": api_key, "Content-Type": "application/json" }
        body = {
            # "caption": message.content,
            "caption": prompt,
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
        # data = requests.get(image_url).content

        # f = open('img01.jpg', 'wb')
        # f.write(data)
        # f.close()
        await message.channel.send(image_url)











    # Send the generated image back to the user
    await message.channel.send(file=discord.File(image, 'generated_image.png'))

def generate_dalle_image(prompt):
    # Use Azure Text Analytics to detect the language of the prompt
    response = text_analytics_client.detect_language([prompt])[0]
    language = response.primary_language.iso6391_name

    # Check if the language is English, as DALL-E currently supports English prompts only
    if language == 'en':
        # Generate image using DALL-E
        # Add your DALL-E code here

        # Placeholder code to generate a random image URL
        image_url = 'https://via.placeholder.com/500x500'  # Replace with actual DALL-E image URL

        # Download the image
        os.system(f'wget {image_url} -O generated_image.png')

        return 'generated_image.png'
    else:
        return None
