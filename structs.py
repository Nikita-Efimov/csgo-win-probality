from bs4 import BeautifulSoup
from scraper import Scraper


class GetTeamRaiting:
    hash_table = {}

    def get(id):
        if id in GetTeamRaiting.hash_table: return GetTeamRaiting.hash_table[id]
        team_page = BeautifulSoup(Scraper.get_html('https://www.hltv.org/team/' + str(id) + '/*'), 'lxml')
        try:
            raiting = int(team_page.find('div', class_='profile-team-stat').find('a').text[1:])
        except AttributeError: raiting = 150
        GetTeamRaiting.hash_table.update({id: raiting})
        return raiting

class Map:
    def __init__(self, name, team1_score, team2_score, enemy_team_id = None):
        self.name = name
        self.team1_score = team1_score
        self.team2_score = team2_score
        self.enemy_team_id = enemy_team_id

class InfoAboutGame:
    # Sizes
    map_name_size = 9
    team_name_size = 14
    coef_size = team_name_size - 1

    # Maps
    maps_names = ['Cache', 'Dust2', 'Mirage', 'Inferno', 'Nuke', 'Train', 'Overpass', 'Vertigo']

    # Prob to coef converation options
    max_percent = 93.5

    def __init__(self, team1_name, team2_name):
        self.team1_name: str = team1_name[:InfoAboutGame.team_name_size - 1]
        self.team2_name: str = team2_name[:InfoAboutGame.team_name_size - 1]

        self.probs: dict = {}
        for map_name in InfoAboutGame.maps_names:
            self.probs.update({map_name: [50, 50]})

    def get_coef_from_prob(prob):
        try: coef = 1 / (prob / InfoAboutGame.max_percent)
        except ZeroDivisionError: coef = 10
        if coef < 1: coef = 1

        # return prob
        return coef

    def print_block(self):
        print(InfoAboutGame.map_name_size * ' ' + '+' + (InfoAboutGame.team_name_size + 1) * '-' + '+' + (InfoAboutGame.team_name_size + 2) * '-' + '+')
        format = '%' + str(InfoAboutGame.team_name_size) + 's'
        print(InfoAboutGame.map_name_size * ' ' + '|' + format % self.team1_name, '|', format % self.team2_name, '|')


        map_name_format = '%8s'

        print(InfoAboutGame.map_name_size * '-' + '+' + '-' * (InfoAboutGame.team_name_size + 1) + '+' + '-' * (InfoAboutGame.team_name_size + 2) + '+')

        for map_name in InfoAboutGame.maps_names:
            team1_prob = self.probs[map_name][0]
            team2_prob = self.probs[map_name][1]
            team1_coef = InfoAboutGame.get_coef_from_prob(team1_prob / ((team1_prob + team2_prob) / 100))
            team2_coef = InfoAboutGame.get_coef_from_prob(team2_prob / ((team1_prob + team2_prob) / 100))

            format = '%' + str(InfoAboutGame.coef_size) + '.2f'
            print(map_name_format % map_name, '|', format % team1_coef, '| ', format % team2_coef, '|')

        print('-' * (InfoAboutGame.map_name_size + InfoAboutGame.coef_size * 2 + 8))
