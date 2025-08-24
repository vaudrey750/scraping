from scaper import init_scraper
from bs4 import BeautifulSoup
import time
import os
from datetime import datetime

from models import MonthGames, Team, Game, TeamScore, Score


def format_date(str_date: str, str_hour: str):
    original_datetime_str = f"{str_date} - {str_hour}"
    mois_fr_to_num = {
    "janv.": "01", "févr.": "02", "mars": "03", "avr.": "04",
    "mai": "05", "juin": "06", "juil.": "07", "août": "08",
    "sept.": "09", "oct.": "10", "nov.": "11", "déc.": "12"
}

    # Découpage personnalisé
    parts = original_datetime_str.split()
    day = parts[1]
    mois = mois_fr_to_num[parts[2]]
    year = parts[3]
    time = original_datetime_str.split("-")[1].strip()

    # Reconstitution d'une chaîne compatible avec datetime
    clean_str = f"{day}/{mois}/{year} {time}"
    date_obj = datetime.strptime(clean_str, "%d/%m/%Y %H:%M")

    # Conversion au format ISO
    return date_obj.strftime("%Y-%m-%dT%H:%M:%S")




class TeamCalendar:

    def __init__(self, url_prefix: str = "saison"):
        """
        """
        BASE_URL=os.getenv("BASE_URL")
        self.url = f"{BASE_URL}/{url_prefix}"
        self.months_games: list[MonthGames] = []
        
    def __extract_score_game(self):
        # Configuration du mode headless
        driver = init_scraper()
        driver.get(self.url)

        for _ in range(10):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            driver.execute_script("window.scrollTo(document.body.scrollHeight, document.body.scrollHeight - 100);")

        # Récupérer le HTML complet
        html = driver.page_source
        driver.quit()

        soup =  BeautifulSoup(html, "html.parser")

        return soup.find_all("div", attrs={"class": "match-score"})
    

    def __get_month_of_games(self, score):
        """
        get month of game
        """
        try:
            return score.find("div", attrs={"class": "ng-star-inserted"}).text.strip()
        except Exception as e:
            raise(f"Game month not found => Error: {e}")


    def __team_details(self, info_score, class_tag):
        """
        """
        try:
            team_parsor = info_score.find("div", attrs={"class": class_tag})
            team_link = team_parsor.find("a", attrs={"class": "team"}).attrs.get("href")
            team_logo = team_parsor.find("img", attrs={"class": "size-xxs"}).attrs.get("src")
            team_name = team_parsor.find("span", attrs={"class": "equipe-name"}).text

            team_status = team_parsor.find("span", attrs={"class": "equipe-statut"})
            is_forfeit = True if team_status and team_status.text == 'Forfait' else False

            return Team(name=team_name, link=team_link, logo=team_logo) , is_forfeit
        except Exception as e:
            raise("team details error: {e}")

    def __get_games(self, score) -> list[Game]:
        games =  score.find_all("app-match-score")

        score_game: list[Game] = []
        for game in games:
            # game info
            game_date = game.find("span", attrs={"class": "schedule-match"}).text
            game_competition = game.find("a", attrs={"class": "text-bold-sm"}).text.strip()
            game_day = game.find("span", attrs={"class": "text-xs"}).text.strip()

            # info score
            info_score = game.find("div", attrs={"class": "info-score"})
            receiver_team, receiver_team_is_forfeit = self.__team_details(info_score, "recevant")
            visitor_team, visitor_team_is_forfeit = self.__team_details(info_score, "visiteur")
            
            # score_zone
            score_zone = game.find("div", attrs={"class": "zone-score"})
            score_zone_a = game.find("a", attrs={"class": "score"})
            game_link = score_zone_a.attrs.get("href") if score_zone_a else None
            
            scores = score_zone.find_all("span", attrs={"class": "digit"})
            receiver_score = int(scores[0].text) if scores else None
            visitor_score = int(scores[1].text) if scores else None

            game_link_details = score_zone.find("a", attrs={"class": "cursor-pointer"}).attrs.get("href")
            game_identifer = game_link_details.split("/")[-1]

            
            game_hour_obj = score_zone.find("span", attrs={"class": "frame uppercase"})
            game_hour = game_hour_obj.text.strip() if game_hour_obj else "09:30"


            ## tir au but
            match_status = game.find("div", attrs={"class": "macth-statut"})
            tabs = match_status.text.replace('TAB', '').split('-') if match_status else None

            score_game.append(
                Game(
                    date = game_date.split('-')[0].strip(),
                    hour = game_hour,
                    link = game_link,
                    day = game_day,
                    season = os.getenv("SAISON"),
                    competition = game_competition.split('-')[0].strip().upper(),
                    game_link_details = game_link_details,
                    game_identifer = game_identifer,
                    receiver = TeamScore(
                        team = receiver_team,
                        score = Score(
                            goal = receiver_score,
                            tab_goal = int(tabs[0].strip()) if tabs else None
                        ),
                        is_forfeit= receiver_team_is_forfeit
                    ),
                    visitor = TeamScore(
                        team = visitor_team,
                        score = Score(
                            goal = visitor_score,
                            tab_goal = int(tabs[1].strip()) if tabs else None
                        ),
                        is_forfeit= visitor_team_is_forfeit
                    )
                )
            )
        return score_game

    def run(self):
        """
        """
        import json
        games_json = []

        scores = self.__extract_score_game()
        for score in scores:
            if score is None:
                continue
            
            month = self.__get_month_of_games(score)
            games = self.__get_games(score)
            self.months_games.append(
               MonthGames(month, games)
            )

            for game in games:
                games_json.append({
                    "game_id": game.game_identifer,
                    "status": "published",
                    "receiver_team": game.receiver.team.name,
                    "receiver_goal": game.receiver.score.goal,
                    "receiver_penalty_goal": game.receiver.score.tab_goal,
                    "receiver_forfeit": game.receiver.is_forfeit,
                    "visitor_team": game.visitor.team.name,
                    "visitor_goal": game.visitor.score.goal,
                    "visitor_penalty_goal": game.visitor.score.tab_goal,
                    "visitor_forfeit": game.visitor.is_forfeit,
                    "game_date": format_date(game.date, game.hour),
                    "league": game.competition,
                    "game_day": game.day.strip(),
                    "season": game.season

                })
        
        with open('games.json', 'w') as fp:
            json.dump(games_json, fp, ensure_ascii=False)


TeamCalendar().run()