import os
import requests
import uuid
import json
from Base import SportEasy
from constants import PLAYER_MAPPING_POSITION, COMPETITIONS


COOKIES = SportEasy.api_login("vaudrey560@gmail.com", "Steff560#")


def get_player_status(team_id=495464):
    """get all player position
    """
    player_positions = []
    player_roles = []
    
    result = requests.get(
        f"https://api.sporteasy.net/v2.2/teams/{team_id}/fields/",
        cookies=COOKIES
    )
    if result:
        result_json = result.json()
        for result in result_json:
            if result.get("id") == "usual_tactic_position":
                for choise in result["parameters"]["choices"]:
                    if not choise[0]:
                        continue
                    player_positions.append({
                        "player_position_id": choise[0],
                        "position": PLAYER_MAPPING_POSITION[choise[1]][0],
                        "position_lv2": choise[1],
                        "view_order": PLAYER_MAPPING_POSITION[choise[1]][1],
                        "status": "published"
                    })
                    
            if result.get("id") == "role":
                for role in result["parameters"]["choices"]:
                    player_roles.append({
                        "member_role_id": str(uuid.UUID(int=role[0])),
                        "name": role[1],
                    })
    
        with open('player_position.json', 'w') as fp:
            json.dump(player_positions, fp)
        

        #with open('player_roles.json', 'w') as fp:
        #    json.dump(player_roles, fp)
        return player_positions, player_roles


    #return player_positions, player_roles
    
# saeson 2023-2024 => 1792180
# saeson 2024-2025 => 1792180
def get_members(team_id=495464, season_id=1792180):
    """get All member
    """
    directus_members = []
    result = requests.get(
        f"https://api.sporteasy.net/v2.3/teams/{team_id}/profiles/?season_id={season_id}",
        cookies=COOKIES
    )
    if result:
        result_json = result.json()
        for result in result_json:
            directus_members.append({
                "member_id": str(result["id"]),
                "first_name": result["first_name"],
                "last_name": result["last_name"],
                "pseudo": result["nickname"] if result["nickname"] else "00",
                "club_id": '551269-supremes-beliers',
                "member_role_id": str(result["role"]),
                "birth_day": result["date_of_birth"],
                "arrival_date": result["year_of_arrival"],
                "status": "published",
            })
        
        with open('members.json', 'w') as fp:
            json.dump(directus_members, fp)
        return directus_members
                

def get_players(team_id=495464, season_id=1792180):
    """get All member
    """
    directus_players = []
    result = requests.get(
        f"https://api.sporteasy.net/v2.3/teams/{team_id}/profiles/?season_id={season_id}",
        cookies=COOKIES
    )
    if result:
        result_json = result.json()
        for result in result_json:
            if result['role'] not in (3, 4, 5):
                continue
            
            player_position = 10
            if result["usual_tactic_position"] != None:
                player_position = result["usual_tactic_position"]

            directus_players.append({
                "player_id": str(result["id"]),
                "member": str(result["id"]),
                "main_picture": "13bcc9c0-f152-4fb3-a397-dada0aaefee0",
                "stat_picture": "13bcc9c0-f152-4fb3-a397-dada0aaefee0",
                "celebration_picture": "13bcc9c0-f152-4fb3-a397-dada0aaefee0",
                "status": "published",
                "position": str(player_position),
                "stat": [{
                    "id": int(f"{result["id"]}{str(os.getenv("SAISON"))[2:4]}"),
                    "player_player_id": str(result["id"]),
                    "season_season_date": os.getenv("SAISON"),
                    "position": player_position,
                    "team": "SENIOR 5"
                }]
            })
        with open('players.json', 'w') as fp:
            json.dump(directus_players, fp)
        return directus_players



def get_player_stats(team_id=495464):
    """get All player stats
    """

       ##"https://api.sporteasy.net/v2.1/teams/495464/stats/all/players/?group=all&role=role_player&season_slug_name=2024-2025"
       # 495464 -> competion_id
       # 2024-2025 -> saison
       # https://api.sporteasy.net/v2.1/teams/495464/stats/1328880/players/?group=all&role=role_player&season_slug_name=2024-2025
       ##

    players = []
    
    competions_by_palyer = {}
    for season, competitions in COMPETITIONS.items():
        index = 0
        for competition, competion_id in competitions.items():
            print(competition, competion_id, season)
            result = requests.get(
                f"https://api.sporteasy.net/v2.1/teams/{team_id}/stats/{competion_id[0]}/players/?group=all&role=role_player&season_slug_name={season}",
                cookies=COOKIES
            )
            
            if result:
                result_json = result.json()
                for player in result_json.get("players", []):
                    player_id = player["player"]["id"]
                    if player_id in (8708185, 8702607, 8886783, 1739191, 8871730):
                        continue

                    if not competions_by_palyer.get(player_id):
                        competions_by_palyer[player_id] = {
                            "player_id": str(player["player"]["id"]),
                            "stat": [],
                        }
                    
                    if len(competions_by_palyer.get(player_id, {}).get("stat", [])) + 1 == index + 1:
                        competions_by_palyer[player_id]["stat"].append((
                            {
                                "id": int(f"{player_id}{season[2:4]}"),
                                "player_player_id": str(player["player"]["id"]),
                                "season_season_date": os.getenv("SAISON"),
                                "competition": []
                            }
                        ))

                    stats = {
                        "id": int(f"{competion_id[1]}{player["player"]["id"]}"),
                        "player_season_id": int(f"{player_id}{season[2:4]}"),
                        "league_name": competition,
                    }
                    # player_saison_id -> int
                    # player_player_id -> str
                    #
                    
                    
                    for result in player["results"]:
                        if result["slug_name"] == "has_attended_strict_sum":
                            stats.update({"play": result["value"]})
                        
                        if result["slug_name"] == "player_match_outcome_victory_sum":
                            stats.update({"win": result["value"]})
                        
                        if result["slug_name"] == "player_match_outcome_tie_sum":
                            stats.update({"draw": result["value"]})
                        
                        if result["slug_name"] == "player_match_outcome_defeat_sum":
                            stats.update({"loose": result["value"]})
                        
                        if result["slug_name"] == "player_goals_strict_sum":
                            stats.update({"goal": result["value"]})
                        
                        if result["slug_name"] == "player_assists_strict_sum":
                            stats.update({"assist": result["value"]})
                        
                        if result["slug_name"] == "man_of_event_strict_sum":
                            stats.update({"man_of_match": result["value"]})
                        
                        if result["slug_name"] == "yellow_cards_strict_sum":
                            stats.update({"yellow_card": result["value"]})
                        
                        if result["slug_name"] == "red_cards_strict_sum":
                            stats.update({"red_card": result["value"]})

                    competions_by_palyer[player_id]['stat'][index]["competition"].append(stats)
                index = 0

    for _, stat in competions_by_palyer.items():
       players.append(stat)
        
    with open('players_with_stats.json', 'w') as fp:
        json.dump(players, fp)
    return players



get_players()