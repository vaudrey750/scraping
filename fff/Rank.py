from .Base import BaseFffScraping
from .constants import MAPPING_CLUB, RANKING_ID
import json


#ranking_id = '411047-cdm-r2' 427562-cdm-r2

class Ranking(BaseFffScraping):
    """
        Get ranking from fff page
    """

    def __init__(
            self,
            ranking_id="427562-cdm-r2",
            competition_id="610385be-ca50-4c43-a08d-f61162868922",
            season_id="8f1aabb6-313d-436f-8522-be9e65b65507"
        ):
        url=f"https://www.fff.fr/competition/engagement/{ranking_id}/phase/1/classement.html?gp_no=2"
        super().__init__(url)
        self.competition_id = competition_id
        self.season_id = season_id

    def get_ranking(self):
        
        datas = []
        try:
            ranking_table = self.soup.find("table", attrs={"data-group": "2", "class": "ranking-group"})
            ranking_tbody = ranking_table.find_all("tr")

            for ranking_tr in ranking_tbody[1:]:
                team_name = ranking_tr.find("td", attrs={"class": "data-team"}).find("span").find("a").text
                pos = int(ranking_tr.find("td", attrs={"class": "data-ranking-cell"}).text)

                datas.append({
                    "competition_ranking_id": RANKING_ID[pos],
                    "competition"   :  self.competition_id,
                    "saeson"        :  self.season_id,
                    "position"      :  pos,
                    "team_id"       :  MAPPING_CLUB.get(team_name.strip()),
                    "points"        :  ranking_tr.find("td", attrs={"class": "data-points"}).text,
                    "play"          :  ranking_tr.find("td", attrs={"class": "data-played"}).text,
                    "win"           :  ranking_tr.find("td", attrs={"class": "data-win"}).text,
                    "draw"          :  ranking_tr.find("td", attrs={"class": "data-draw"}).text,
                    "lose"          :  ranking_tr.find("td", attrs={"class": "data-lost"}).text,
                    "forfeit"       :  ranking_tr.find("td", attrs={"class": "data--mystery"}).text,
                    "goal_for"      :  ranking_tr.find("td", attrs={"class": "data-goal-for"}).text,
                    "goal_against"  :  ranking_tr.find("td", attrs={"class": "data-goal-against"}).text,
                    "goal_penalty"  :  ranking_tr.find("td", attrs={"class": "data-penalty"}).text,
                    "goal_diff"     :  ranking_tr.find("td", attrs={"class": "data--goal-diff"}).text,
                    "status"        : "published"
                })
            
        except Exception as e:
            print(e)
        
        with open('fff_ranking.json', 'w') as fp:
                json.dump(datas, fp)
        return datas
