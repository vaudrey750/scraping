from directus_sdk_py import DirectusClient
from fff import ClubCalendar, Rank
from sport_easy import UserApi
import os

client = DirectusClient(
    url=os.getenv("URL"),
    token=os.getenv("TOKEN")
)

def update_items(collection, items, item_id):
    print(f'{collection} begin!')
    
    for item in items:
        client.update_item(
            collection_name=collection, 
            item_id=item[item_id], 
            item_data=item
        )

    print(f'{collection} updated successfully!')


#query = {
#    "filter[palyer_id][_eq]": "00000000-0000-0000-0000-00000080da84",
#    "fields": ["palyer_id", "team_id.name"]
#}

#items = client.get_items("players", query)


def update_ranking():
    items = Rank.Ranking().get_ranking()
    update_items('competition_ranking', items, 'competition_ranking_id')

def update_player_stats():
    items = UserApi.get_player_stats()
    update_items('players', items, 'palyer_id')


def update_player():
    items = UserApi.get_players()
    update_items('players', items, 'palyer_id')


def update_member():
    items = UserApi.get_members()
    update_items('members', items, 'member_id')


def update_calendar():
    items = ClubCalendar.Club().get_all_games()
    update_items('competition_games', items, 'competition_game_id')



update_calendar()
update_ranking()

update_member()
update_player()
update_player_stats()
