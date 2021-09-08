import requests
from bs4 import BeautifulSoup
import json
import unicodedata
import re
from joblib import Parallel, delayed

from typing import List


class Skin:
    def __init__(self, champion_name: str) -> None:
        self.champion_name = champion_name
        self.audio_list = []
        self.champion_image_url = ""

    def add_to_audio_list(self, audio):
        self.audio_list.append(audio)

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class Champion:
    def __init__(self, skin_list: List[Skin]) -> None:
        self.skin_list = skin_list

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=5)


class ChampionRootList:
    def __init__(self, champion_list: List[Champion]) -> None:
        self.champion_list = champion_list

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=5)


class Audio:
    def __init__(self, audio_name: str, audio_url: str) -> None:
        self.audio_name = audio_name
        self.audio_url = audio_url

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=1)


class SubSection:
    def __init__(self, subsection_name: str) -> None:
        self.subsection_name = subsection_name
        self.audio_list = []

    def append_to_audio(self, audio: Audio):
        self.audio_list.append(audio)

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=2)


class Section:
    def __init__(self, section_name: str) -> None:
        self.subsection_list = []
        self.audio_list = []
        self.section_name = section_name

    def append_to_subsection(self, subsection: SubSection):
        self.subsection_list.append(subsection)

    def append_to_audio(self, audio: Audio):
        self.audio_list.append(audio)

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=3)


class Image:
    def __init__(self, name: str, url: str) -> None:
        self.name = name
        self.url = url

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=1)

class ImageList:
    def __init__(self, image_list: List[Image]):
        self.image_list = image_list

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=1)


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
            champion_name = champion_url.split("/")[2]
            if champion_name == "Nunu_%26_Willump":
                champion_url = "/wiki/{}/LoL".format("Nunu")
            champion_list.append(champion_url)
        except:
            print("No champion in this one")
    return champion_list[1:]


def get_champion_data_for_champion_url(champion_url):
    # main_path = os.path.join(os.getcwd(), str(champion_url).split("/")[2])
    # os.mkdir(main_path)
    champion_name = champion_url.split("/")[2].split("_")
    champion_url = "https://leagueoflegends.fandom.com" + champion_url + "/Audio"

    page = requests.get(champion_url)

    soup = BeautifulSoup(page.content, "html.parser")

    main_div = soup.find(class_="mw-parser-output")

    section_list = []
    skin_names = []
    section = None
    skin_name = None
    if (main_div is None):
        print("Main div is none for Champion {} so cannot create the json".format(champion_url))
        return None
    for element in main_div.findAll(recursive=True):
        if (element.name == 'h2'):
            if (not (section == None)):
                section_list.append(section)
            section = Section(element.text)
        elif (element.name == 'dl'):
            if (not (section == None)):
                section.append_to_subsection(SubSection(element.text))
        elif (element.name == 'ul'):
            audio_elements = element.find_all("audio")
            for audio_element in audio_elements:
                audio_url = audio_element.find("source")['src']
                audio_name = str(audio_url).split("/")[7]
                audio_name_dess = audio_name.split("_")
                if len(audio_name_dess) == 1:
                    audio_name_dess = audio_name_dess[0].split(".")
                if not (champion_name[0] in audio_name):
                    skin_temp_arr = audio_name.split(".")  # Beacuse it can be like TrueDamage.SpawnMusic.ogg
                    skin_name = skin_temp_arr[0] + "_" + skin_temp_arr[1]
                else:
                    skin_name = "_".join(audio_name_dess).replace(".ogg", "")
                if not (skin_name == None):
                    if skin_name not in skin_names:
                        skin_names.append(skin_name)
                if (not (section == None)):
                    if (not (section.subsection_list)):
                        section.append_to_audio(Audio(audio_name, audio_url))
                    else:
                        section.subsection_list[-1].append_to_audio(Audio(audio_name, audio_url))

    skins_list = []

    for skin_name in skin_names:
        skin = Skin("_".join(skin_name.split("_")[:len(champion_name) + 1]))
        for section in section_list:
            for audio in section.audio_list:
                if skin.champion_name in audio.audio_name:
                    skin.add_to_audio_list(audio)
            for subsection in section.subsection_list:
                for audio_sub in subsection.audio_list:
                    if skin_name in audio_sub.audio_name:
                        skin.add_to_audio_list(audio_sub)
        skins_list.append(skin)
    print("Done: ", champion_name)

    all_champions_page = "https://leagueoflegends.fandom.com/wiki/List_of_champions"
    page = requests.get(all_champions_page)
    soup = BeautifulSoup(page.content, "html.parser")
    name_for_image = str(champion_url).split("/")[4].replace("_", " ").replace("%27", "'")
    champion = Champion(skins_list)
    open("{}.json".format(champion_name), 'wb').write(str.encode(champion.to_json()))
    return Champion(skins_list)


def make_skin_json(champion_root_list):
    page = requests.get("https://leagueoflegends.fandom.com/wiki/List_of_skins_by_champion")
    champion_names = []
    for champion_url in get_champion_list():
        champion_name = champion_url.split("/")[2].split("_")
        champion_names.append(" ".join(champion_name))

    soup = BeautifulSoup(page.content, 'html.parser')
    main_table = soup.find("table")
    image_list = []
    skip_first = False
    for table_row in main_table.find_all("tr"):
        if not skip_first:
            skip_first = True
            continue
        img_tag_list = table_row.find_all("img")
        for img_tag in img_tag_list:
            try:
                image_list.append(Image(img_tag['alt'].replace(".png", ""), img_tag['data-src'].replace("/26", "/40")))
            except:
                image_list.append(Image(img_tag['alt'].replace(".png", ""), img_tag['src'].replace("/26", "/40")))

    image_root_list = ImageList(image_list)

    open("{}.json".format("all_champions"), 'wb').write(str.encode(image_root_list.to_json()))


champion_list = []

input_champion_list = get_champion_list()


for champion_url in get_champion_list():
    champion_list.append(get_champion_data_for_champion_url(champion_url))

champion_root_list = ChampionRootList(champion_list)

make_skin_json(champion_root_list)
