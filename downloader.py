# 1) A folder for each champion e.g. Aatrox, Ahri etc
# 2) Within that, a folder for each skin
# 3) Then within that, a folder for each action like Champion Select, Movement, First Encounter
# 4) Then within that, Folder for each sub one e.g. Pick and Ban for CHampion Select, Movement has First move with enemy pantheon etc
# 5) and then within each of those the respective audio :) the title of each audio is from website

import requests
from bs4 import BeautifulSoup

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

for attribute in voice_div.find_all(recursive=False):
    if (attribute.name == "h2"):
        print("Found Main headline:", attribute.text)
    elif (attribute.name == "dl"):
        print("Found sub headline:", attribute.text)