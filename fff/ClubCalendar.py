from datetime import datetime
import locale
from .Base import BaseFffScraping
from bs4 import BeautifulSoup
from requests import get
from .constants import MAPPING_CLUB, COMPETITION
import uuid
import json

# saeson = 2024112966SEM2
# team_id = 551269-supremes-beliers
# 

class Club(BaseFffScraping):
    """Get list of supreme belier game from fff page
    """

    def __init__(self, 
                 team_id="551269-supremes-beliers", 
                 saeson="2024112966SEM2", 
                 competition_id="610385be-ca50-4c43-a08d-f61162868922", 
                 saeson_id="8f1aabb6-313d-436f-8522-be9e65b65507"
    ):
        url=f"https://www.fff.fr/competition/club/{team_id}/equipe/{saeson}/resultats-et-calendrier.html"
        super().__init__(url)
        self.competition_id = competition_id
        self.saeson_id = saeson_id
    
    def __extract_info(self, url_prefix):
        extract_info = {}
        
        full_url = f"https://www.fff.fr{url_prefix}"
        extract_page = get(full_url)
        extract_soup = BeautifulSoup(extract_page.content, "lxml")
        stadium_name = extract_soup.find("p", attrs={"class": "stadium-name"}).text
        addresses = extract_soup.find_all("p", attrs={"class": "stadium-adress"})
        for index, adr in enumerate(addresses):
            extract_info.update({f"address_{index + 1}": adr.text.strip()})
        extract_info.update({"stadium_name": stadium_name.strip()})
        return extract_info


    def get_all_games(self):

        datas = []
        sb_months_games = self.soup.find_all("div", attrs={"class": "container_elem_carousel"})
        base_id = 1
        for sb_month_game in sb_months_games:
            
            get_resultats = sb_month_game.find_all("div", attrs={"class": "resultat"})
            for get_resultat in get_resultats:
                
                competition = get_resultat.find("h3",  attrs={"class": "season__title--compet"}).text

                competition_name = competition.split("-")[0].strip().upper()
                journee = get_resultat.find("h3",  attrs={"class": "season__title--journee"}).text
                
                aside_resultats = get_resultat.find_all("div", attrs={"class": "aside_resultat__match"})
                
                for aside_resultat in aside_resultats:
                    visitor_team_status = None
                    local_team_status = None
                    
                    extract_tag = aside_resultat.find("a", attrs={"class": "aside-resultat__match-item"}).attrs.get("href")
                    extract_info = self.__extract_info(extract_tag)

                    local_team_name = aside_resultat.find("div", attrs={"class": "aside-resultat_team aside-resultat_team--home"}).text
                    if "Forfait Général" in local_team_name:
                        local_team_status = "Forfait Général"
                        local_team_name = local_team_name.replace("Forfait Général", "")
                    try: 
                        local_team_score = int(aside_resultat.find("b", attrs={"class": "score score_domicile flex flex_ai_center"}).text)
                        local_team_status = "Play"
                    except Exception as e: 
                        local_team_score = None
                        
                    try:
                        tab = aside_resultat.find("b", attrs={"class": "extra-time extra-time__penalty"}).text
                        tab = tab.replace("T.A.B.", "").split("-")
                        local_tab = int(tab[0].strip())
                        visitor_tab = int(tab[1].strip())
                    except Exception as e:
                        local_tab = None
                        visitor_tab = None
                    
                    visitor_team_name = aside_resultat.find("div", attrs={"class": "aside-resultat_team aside-resultat_team--away"}).text
                    if "Forfait Général" in visitor_team_name:
                        visitor_team_status = "Forfait Général"
                        visitor_team_name = visitor_team_name.replace("Forfait Général", "")
                    try:
                        visitor_team_score = int(aside_resultat.find("b", attrs={"class": "score score_exterieur flex flex_ai_center"}).string)
                        visitor_team_status = "Play"
                    except Exception as e:
                        visitor_team_score = None
                    
                    game_date_hour = journee.replace("Senior 5 - ", "").strip().split("-")
                    addr_3 = extract_info.get('address_3') if extract_info.get('address_3') else ''
                    addr_4 = extract_info.get('address_4') if extract_info.get('address_4') else ''
                    address = f"{extract_info.get('address_1')} {extract_info.get('address_2')} {addr_3} {addr_4}".upper()

                    date_txt = f"{game_date_hour[0].strip()} {game_date_hour[1].strip()}"

                    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
                    datas.append({
                        "competition_game_id":  str(uuid.UUID(int=base_id)),
                        "local_team_id": MAPPING_CLUB.get(local_team_name.strip()),
                        "local_team_score": local_team_score,
                        "local_team_penalty_score": local_tab,
                        "local_team_status": local_team_status,

                        "visitor_team_id": MAPPING_CLUB.get(visitor_team_name.strip()),
                        "visitor_team_score": visitor_team_score,
                        "visitor_team_penalty_score": visitor_tab,
                        "visitor_team_status": visitor_team_status,

                        "competition_day": competition.split("-")[1].split("/")[1].strip(),
                        "game_date": datetime.strptime(date_txt, "%A %d %B %Y %H:%M").strftime("%Y-%m-%d %H:%M:%S"),
                        "game_adress": address,
                        "competition": COMPETITION[competition_name], # self.competition_id,
                        "season": self.saeson_id,
                        "status": "published"
                    })
                    base_id += 1
        with open('fff_all_game.json', 'w') as fp:
            json.dump(datas, fp)
        return datas
