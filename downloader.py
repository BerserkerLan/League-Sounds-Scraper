# 1) A folder for each champion e.g. Aatrox, Ahri etc
# 2) Within that, a folder for each skin
# 3) Then within that, a folder for each action like Champion Select, Movement, First Encounter
# 4) Then within that, Folder for each sub one e.g. Pick and Ban for CHampion Select, Movement has First move with enemy pantheon etc
# 5) and then within each of those the respective audio :) the title of each audio is from website

import requests
from bs4 import BeautifulSoup
import os

class Sound:
    def __init__(self, title, sound_url):
        self.title = title
        self.sound_url = sound_url

class Action:
    def __init__(self, action_title, sounds_list):
        self.action_title = action_title
        self.sounds_list = sounds_list

aatrox_url = "https://leagueoflegends.fandom.com/wiki/Aatrox/LoL/Audio"

page = requests.get(aatrox_url)

soup = BeautifulSoup(page.content, "html.parser")

voice_div = soup.find(class_="mw-parser-output")

# main_headlines = voice_div.find_all("h2") # So that we only get the main headlines for 3)

# for headline in main_headlines:
#     print(headline.text) # this has all the main headlines for 3) but also has the ones for 4) :( also doesn't have pick ban titles)

action_list = []
sound_list = []
current_path = os.getcwd()
current_inner_path = os.getcwd()
current_inner_inner_path = os.getcwd()

for attribute in voice_div.find_all(recursive=False):
    if (attribute.name == "h2"):
        current_path = os.path.join(os.getcwd(), attribute.text)
        current_inner_path = os.path.join(current_path)
        # print("1Path is now:", current_path)
        os.mkdir(current_path)
    elif (attribute.name == "h3"):
        current_inner_path = os.path.join(current_path, attribute.text)
        current_inner_inner_path = os.path.join(current_inner_path)
        # print("2Path is now:", current_inner_inner_path)
        os.mkdir(current_inner_inner_path)
    elif (attribute.name == "dl"):
        current_inner_inner_path = os.path.join(current_inner_path, attribute.text)
        # print("3Path is now:", current_inner_inner_path)
        os.mkdir(current_inner_inner_path)
    elif (attribute.name == "ul"):
        i = 0
        for voice_attribute in (attribute.find_all("li")):
            sound_url = voice_attribute.find("audio").find("source")['src']
            # print("Found voice:",voice_attribute.text, "with url", sound_url)
            sound_request = requests.get(sound_url)
            complete_save_path = os.path.join(current_inner_inner_path, str(voice_attribute.text) + '.mp3')
            i += 1
            open(complete_save_path, 'wb').write(sound_request.content)
            # print("Path to save it is:",complete_save_path)