#Made by Felix (Blobtoe)

import json
import os
import time
import base64
from imgurpython import ImgurClient
from discord_webhook import DiscordWebhook, DiscordEmbed
import requests
from datetime import datetime


#######################################
#sends a message to a discord webhook given the json file for the pass and the webhook url
def discord_webhook(path, webhook_url):
    print("sharing to discord")

    #load the json file from the pass
    with open(path) as f:
        data = json.load(f)

    #send a message with the discord webhook
    webhook = DiscordWebhook(url=webhook_url,
                             username="Blobtoe's Kinda Crappy Images")
    embed = DiscordEmbed(title=data["satellite"],
                         description="Pass over Vancouver, Canada",
                         color=242424)
    embed.add_embed_field(name='Max Elevation',
                          value=str(data["max_elevation"]) + "°")
    embed.add_embed_field(name='Frequency',
                          value=str(data["frequency"]) + " Hz")
    embed.add_embed_field(name="Duration",
                          value=str(round(data["duration"])) + " seconds")
    embed.add_embed_field(
        name='Pass Start',
        value=datetime.utcfromtimestamp(
            data["aos"]).strftime("%B %-d, %Y at %-H:%M:%S UTC"))
    embed.add_embed_field(name='Sun Elevation',
                          value=str(data["sun_elev"]) + "°")
    embed.set_image(url=data["main_image"])

    #add all the image links
    links_string = ""
    for link in data["links"]:
        links_string += "[{}]({}), ".format(link, data["links"][link])
    embed.add_embed_field(name="Other Image Links", value=links_string)

    webhook.add_embed(embed)
    response = webhook.execute()

    print("done")
    return response


#######################################
#uploads an image to imgur given the json file for the pass and the image's file path, then returns the link
def imgur(path, image):
    print("sharing to imgur")

    #check if the file exists
    if os.path.isfile(image) == False:
        print("Error: Image does not exists.")
        return

    #create title for imgur post
    with open(path) as f:
        data = json.load(f)
        title = "{} at {}° at {}".format(data["satellite"],
                                         data["max_elevation"], data["aos"])

    #get imgur credentials from secrets.json
    with open("/home/pi/website/weather/scripts/secrets.json") as f:
        data = json.load(f)
        client_id = data["imgur_id"]
        client_secret = data["imgur_secret"]

    client = ImgurClient(client_id, client_secret)
    config = {'name': title, 'title': title}

    #try 10 times to upload image
    count = 0
    while True:
        try:
            img = client.upload_from_path(image, config=config)
            link = img["link"]
            print("done")
            return link
        except Exception as e:
            count += 1
            print(
                "failed to upload image... trying again  {}/10".format(count))
            print(e)
            time.sleep(2)

            if count >= 10:
                return None


#######################################
#uploads an image to imgbb.com given the image's file pathm, then return a link
def imgbb(image):
    with open(image, "rb") as file:
        with open("/home/pi/website/weather/scripts/secrets.json") as s:
            payload = {
                "key": json.load(s)["imgbb_id"],
                "image": base64.b64encode(file.read()),
            }
        for i in range(1, 11):
            try:
                res = requests.post("https://api.imgbb.com/1/upload",
                                    payload,
                                    timeout=400,
                                    verify=False)
                data = json.loads(res.content)
                return data["data"]["url"]
            except Exception as e:
                print(f"failed to upload image... trying again  {i}/10")
                print(e)
                time.sleep(2)
        return None
        
