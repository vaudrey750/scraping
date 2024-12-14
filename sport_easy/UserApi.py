import requests
import uuid
import json
from .Base import SportEasy
from .constants import PLAYER_MAPPING_POSITION


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
                        "player_position_id": str(uuid.UUID(int=choise[0])),
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
        

        with open('player_roles.json', 'w') as fp:
            json.dump(player_roles, fp)
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
                "member_id": str(uuid.UUID(int=result["id"])),
                "first_name": result["first_name"],
                "last_name": result["last_name"],
                "speudo": result["nickname"] if result["nickname"] else "00",
                "club_id": "5e92732e-8be4-4109-a004-1996fc62101b",
                "member_role_id": str(uuid.UUID(int=result["role"])),
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
            

            player_position = "bb1588f7-176f-40e6-b219-fe4d2851187a"
            if result["usual_tactic_position"] != None:
                player_position = str(uuid.UUID(int=result["usual_tactic_position"]))
            directus_players.append({
                "palyer_id": str(uuid.UUID(int=result["id"])),
                "member_id": str(uuid.UUID(int=result["id"])),
                "player_position_id": player_position,
                "team_id": "c28e83b4-b72b-40a5-90cd-2f95fd3040b5",
                "player_saeson": [{
                    "id": result["id"],
                    "saesons_season_id": "8f1aabb6-313d-436f-8522-be9e65b65507",
                    "players_palyer_id": str(uuid.UUID(int=result["id"])),
                    "play": 0,
                    "win": 0,
                    "draw": 0,
                    "lose": 0,
                    "goals": 0,
                    "assists": 0,
                    "man_of_match": 0,
                    "yellow_card": 0,
                    "clean_sheet": 0,
                }],
                "status": "published",
            })
        with open('players.json', 'w') as fp:
            json.dump(directus_players, fp)
        return directus_players



def get_player_stats(team_id=495464, season_id="2024-2025"):
    """get All player stats
    """

    players = []
    result = requests.get(
        f"https://api.sporteasy.net/v2.1/teams/{team_id}/stats/all/players/?group=all&role=role_player&season_slug_name={season_id}",
        cookies=COOKIES
    )
    if result:
        result_json = result.json()
        for player in result_json.get("players", []):
            
            
            current_player = {
                "palyer_id": str(uuid.UUID(int=player["player"]["id"])),
                "player_saeson": []
            }
            player_saeson = {}
            for result in player["results"]:
                player_saeson.update({"id": player["player"]["id"]})
                if result["slug_name"] == "has_attended_strict_sum":
                    player_saeson.update({"play": result["value"]})
                
                if result["slug_name"] == "player_match_outcome_victory_sum":
                    player_saeson.update({"win": result["value"]})
                
                if result["slug_name"] == "player_match_outcome_tie_sum":
                    player_saeson.update({"draw": result["value"]})
                
                if result["slug_name"] == "player_match_outcome_defeat_sum":
                    player_saeson.update({"lose": result["value"]})
                
                if result["slug_name"] == "player_goals_strict_sum":
                    player_saeson.update({"goals": result["value"]})
                
                if result["slug_name"] == "player_assists_strict_sum":
                    player_saeson.update({"assists": result["value"]})
                
                if result["slug_name"] == "man_of_event_strict_sum":
                    player_saeson.update({"man_of_match": result["value"]})
                
                if result["slug_name"] == "yellow_cards_strict_sum":
                    player_saeson.update({"yellow_card": result["value"]})
                
                if result["slug_name"] == "red_cards_strict_sum":
                    player_saeson.update({"red_card": result["value"]})

                current_player.update({"player_saeson": [player_saeson]})
            players.append(current_player)
                
        with open('players_with_stats.json', 'w') as fp:
            json.dump(players, fp)
        return players
