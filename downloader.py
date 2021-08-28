import requests
from bs4 import BeautifulSoup
import json
import unicodedata
import re

class ChampionRootList:
    def __init__(self, champion_list) -> None:
        self.champion_list = champion_list
    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=5)
class Champion:
    def __init__(self, champion_name, section_list, champion_image_url) -> None:
        self.champion_name = champion_name
        self.section_list = section_list
        self.image_url = champion_image_url
    def __str__(self) -> str:
        return "Champion Name: {}, List Of Sections: {}".format(self.champion_name, self.section_list)
    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

class Section:
    def __init__(self, section_name) -> None:
        self.subsection_list = []
        self.audio_list = []
        self.section_name = section_name
    def append_to_subsection(self, subsection):
        self.subsection_list.append(subsection)
    def append_to_audio(self, audio):
        self.audio_list.append(audio)
    def __str__(self) -> str:
        return "Section Name: {}, Section audio list: {}, section subsection list: {}".format(self.section_name, self.audio_list, self.subsection_list)
    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=3)

class SubSection:
    def __init__(self, subsection_name) -> None:
        self.subsection_name = subsection_name
        self.audio_list = []
    def append_to_audio(self, audio):
        self.audio_list.append(audio)
    def __str__(self) -> str:
        return "SubSection Name: {}, SubSection audio list: {}".format(self.section_name, self.audio_list)
    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=2)

class Audio:
    def __init__(self, audio_name, audio_url) -> None:
        self.audio_name = audio_name
        self.audio_url = audio_url
    def __str__(self) -> str:
        return "Audio Name: {}, Audio Url: {}".format(self.audio_name, self.audio_url)
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
    champion_url = "https://leagueoflegends.fandom.com" + champion_url + "/Audio"

    page = requests.get(champion_url)

    soup = BeautifulSoup(page.content, "html.parser")

    main_div = soup.find(class_="mw-parser-output")

    # tabber = soup.find(class_="tabber wds-tabber")

    section_list = []
    section = None
    if (main_div is None):
        print("Main div is none for Champion {} so cannot create the json".format(champion_url))
        return None
    for element in main_div.findAll(recursive=True):
        if (element.name == 'h2'):
            if (not(section == None)):
                section_list.append(section)
            section = Section(element.text)
        elif (element.name == 'dl'):
            if (not(section == None)):
                section.append_to_subsection(SubSection(element.text))
        elif (element.name == 'ul'):
            audio_elements = element.find_all("audio")
            for audio_element in audio_elements:
                audio_url = audio_element.find("source")['src']
                audio_name = str(audio_url).split("/")[7]
                if (not(section == None)):
                    if (not (section.subsection_list)):
                        section.append_to_audio(Audio(audio_name, audio_url))
                    else:
                        section.subsection_list[-1].append_to_audio(Audio(audio_name, audio_url))

    #Now to get the champion cover image URL
    # champion_url_for_image = "https://leagueoflegends.fandom.com/wiki/Category:{}".format(str(champion_url).split("/")[4])
    # page = requests.get(champion_url_for_image)
    # soup = BeautifulSoup(page.content, "html.parser")
    # image_url = soup.find(class_="mw-parser-output").find("img")['src']

    #/html/body/div[4]/div[3]/div[5]/main/div[3]/div[2]/div[1]/table[2]

    all_champions_page = "https://leagueoflegends.fandom.com/wiki/List_of_champions"
    page = requests.get(all_champions_page)
    soup = BeautifulSoup(page.content, "html.parser")
    name_for_image = str(champion_url).split("/")[4].replace("_"," ").replace("%27","'")
    if (name_for_image == "Nunu"): 
        name_for_image = "Nunu & Willump"
    try:
        image_url = soup.find(title=name_for_image).find("img")['data-src']
    except:
        import pdb; pdb.set_trace()
    print("Done Champion: {}".format(champion_url))
    return Champion(champion_url, section_list, image_url)

    #mw-content-text > div.mw-parser-output > div.tabber.wds-tabber > div.wds-tab__content.wds-is-current > ul:nth-child(5) > li:nth-child(1) > i

    #mw-content-text > div.mw-parser-output > div.tabber.wds-tabber > div:nth-child(3) > ul:nth-child(5) > li:nth-child(1) > i

    #mw-content-text > div.mw-parser-output > ul:nth-child(4) > li > i

    # all_audio_elements = soup.find_all("audio")

    # for audio_element in all_audio_elements:
    #     try:
    #         audio_url = audio_element.find("source")['src']
    #         audio_name_list = str(audio_url).split("/")
    #         print(audio_name_list[7])
    #         audio_request = requests.get(audio_url)
    #         open(os.path.join(main_path, slugify(str(audio_name_list[7]) + '.mp3')), 'wb').write(audio_request.content)
    #     except Exception as e:
    #         print("Bad", e)

champion_list = []

for champion_url in get_champion_list():
    champion_list.append(get_champion_data_for_champion_url(champion_url))

# champion_list.append(get_champion_data_for_champion_url("/wiki/Lee_Sin/LoL"))

champion_root_list = ChampionRootList(champion_list)

open("custom.json", 'wb').write(str.encode(champion_root_list.to_json()))