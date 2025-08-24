from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class Serie(Enum):
    Victory = "V"
    DRAW = "n"
    LOOSE = "d"


@dataclass
class Score:
    goal: int
    tab_goal: int


@dataclass
class Team:
    name: str
    link: str
    logo: str


@dataclass
class TeamScore:
    team: Team
    score: Score
    is_forfeit: bool = False


@dataclass
class Game:
    date: str
    hour: str
    link: str
    day: str
    season: str
    game_link_details: str
    game_identifer: str
    competition: str
    receiver: TeamScore
    visitor: TeamScore


@dataclass
class MonthGames:
    month: str
    games: list[Game]


@dataclass
class TeamRanking:
    position: int
    team: Team
    points: int
    play: int
    win: int
    draw: int
    loose: int
    forfeit: int
    penality: int
    goal: int
    conceded: int
    goal_diff: int
    current_serie: list[Serie]
