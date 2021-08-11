import requests
from bs4 import BeautifulSoup
import os
import unicodedata
import re

def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')


def get_champion_list():
    champion_list = []
    champion_list_url = "https://leagueoflegends.fandom.com/wiki/List_of_champions"
    page = requests.get(champion_list_url)
    soup = BeautifulSoup(page.content, "html.parser")
    table_main = soup.find(class_="article-table sticky-header sortable").find_all("tr")
    for elem in table_main:
        try:
            champion_url = elem.find_all("a")[1]['href']
            champion_list.append(champion_url)
        except:
            print("No champion in this one")
    print(champion_list[1:])
    return champion_list[1:]

def download_sound_for_champion(champion_name):
    main_path = os.path.join(os.getcwd(), str(champion_name).split("/")[2])
    os.mkdir(main_path)
    champion_url = "https://leagueoflegends.fandom.com" + champion_name + "/Audio"

    page = requests.get(champion_url)

    soup = BeautifulSoup(page.content, "html.parser")

    all_audio_elements = soup.find_all("audio")

    for audio_element in all_audio_elements:
        try:
            audio_url = audio_element.find("source")['src']
            audio_name_list = str(audio_url).split("/")
            print(audio_name_list[7])
            audio_request = requests.get(audio_url)
            open(os.path.join(main_path, slugify(str(audio_name_list[7]) + '.mp3')), 'wb').write(audio_request.content)
        except Exception as e:
            print("Bad", e)

for champion_url in get_champion_list():
    download_sound_for_champion(champion_url)