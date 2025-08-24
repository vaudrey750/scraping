import os
import time

from scaper import init_scraper
from bs4 import BeautifulSoup

from models import TeamRanking, Team, Serie


class Ranking:

    def __init__(self, url_prefix: str = "classement"):
        """
        """
        BASE_URL= os.getenv("BASE_URL")
        self.url = f"{BASE_URL}/{url_prefix}"
        self.team_ranks: list[TeamRanking] = []

    
    def __extract_ranking(self):
        driver = init_scraper()
        driver.get(self.url)
        time.sleep(3)

        # Récupérer le HTML complet
        html = driver.page_source

        driver.quit()
        soup =  BeautifulSoup(html, "html.parser")
        return soup.find("div", attrs={"id": "tab-group-0-panel-2"})
    
    def __get_rank_info(self, rank) -> TeamRanking:
        """
        """
        position = rank.find("td", attrs={"class": "cdk-column-classement"}).text.strip()
        team_info = rank.find("td", attrs={"class": "cdk-column-nomEquipe"})
        team_info_a = team_info.find("a")
        team = Team(
            name=team_info_a.text.strip(),
            link=team_info_a.attrs.get("href"), 
            logo=team_info_a.find("img", attrs={"class": "size-xs"}).attrs.get("src")
        )
        points = rank.find("td", attrs={"class": "cdk-column-points"}).text.strip()
        play = rank.find("td", attrs={"class": "cdk-column-nbMatch"}).text.strip()
        win = rank.find("td", attrs={"class": "cdk-column-nbMatchGagne"}).text.strip()
        draw = rank.find("td", attrs={"class": "cdk-column-nbMatchNul"}).text.strip()
        loose = rank.find("td", attrs={"class": "cdk-column-nbMatchPe"}).text.strip()
        forfeit = rank.find("td", attrs={"class": "cdk-column-nbMatchFo"}).text.strip()
        penality = rank.find("td", attrs={"class": "cdk-column-nbPointPenalite"}).text.strip()
        goal = rank.find("td", attrs={"class": "cdk-column-nbButPour"}).text.strip()
        conceded = rank.find("td", attrs={"class": "cdk-column-nbButContre"}).text.strip()
        goal_diff = rank.find("td", attrs={"class": "cdk-column-diffBut"}).text.strip()
        current_series = rank.find("td", attrs={"class": "cdk-column-serieEnCours"})
        series = current_series.find_all("div", attrs={"class": "ng-star-inserted"})
        status: list[Serie] = []
        for serie in series:
            status.append(
                serie.attrs.get("class")[0]
            )

        return TeamRanking(
            position=position,
            team=team,
            points=points,
            play=play,
            win=win,
            draw=draw,
            loose=loose,
            forfeit=forfeit,
            penality=penality,
            goal=goal,
            conceded=conceded,
            goal_diff=goal_diff,
            current_serie=status
        )

    def run(self):
        """
        """
        import json
        table = self.__extract_ranking()

        ranking_json = []
        ranking = table.find_all("tr", attrs={"class": "cdk-row"})
        for rank in ranking:
            val = self.__get_rank_info(rank)
            self.team_ranks.append(val)
            ranking_json.append({
                "position": val.position,
                "team": val.team.name,
                "point": val.points.replace("FG", "0"),
                "play": val.play,
                "win": val.win,
                "draw": val.draw,
                "loose": val.loose,
                "forfeit": val.forfeit,
                "penality": val.penality,
                "scored": val.goal,
                "conceded": val.conceded,
                "goal_diff": val.goal_diff,
                "competition": "CDM R2",
                #"current_serie": val.current_serie,
                "season": "2024",
                "status": "published"
            })


        with open('ranking.json', 'w') as fp:
            json.dump(ranking_json, fp, ensure_ascii=False)


Ranking().run()


