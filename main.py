from time import time
from bs4 import BeautifulSoup
from scraper import Scraper
from structs import InfoAboutGame, Map, GetTeamRaiting


def main():
    # link = str(input())
    link = 'https://www.hltv.org/matches/2332796/furia-vs-luminosity-ecs-season-7-north-america-week-3'
    parse_match(link)

def parse_match(link):
    soup = BeautifulSoup(Scraper.get_html(link), 'lxml')

    iag = InfoAboutGame(get_names(soup)[0], get_names(soup)[1])

    check_last_games(soup, iag)

    iag.print_block()

def check_last_games(page_src, iag):
    team1_id = page_src.find('div', class_='team1-gradient').find('a').get('href').split('/')[2]
    team2_id = page_src.find('div', class_='team2-gradient').find('a').get('href').split('/')[2]

    print(team1_id)
    check_last_team_games(team1_id, iag, 0)
    print(team2_id)
    check_last_team_games(team2_id, iag, 1)

def check_last_team_games(team_id, iag, iag_pos):
    short_to_long_maps_names = {'cch': 'Cache', 'd2': 'Dust2', 'mrg': 'Mirage', 'inf': 'Inferno', 'nuke': 'Nuke', 'trn': 'Train', 'ovp': 'Overpass', 'vrt': 'Vertigo'}

    home_team_raiting = GetTeamRaiting.get(team_id)

    team_results = BeautifulSoup(Scraper.get_html('https://www.hltv.org/results?team=' + str(team_id)), 'lxml')
    for container in team_results.find_all('div', class_='results-sublist'):
        try:
            date = int(str(container.find('div', class_='result-con').get('data-zonedgrouping-entry-unix'))[:10])
        except ValueError: date = time()
        actual_coef = date / time()
        # print('Time:', date, actual_coef)
        for result in container.find_all('div', class_='result-con'):
            map_text = result.find('div', class_='map-text').text

            enemy_team_id = result.find('div', class_='team2').find('img', class_='team-logo').get('src').split('/')[6]
            enemy_team_raiting = GetTeamRaiting.get(enemy_team_id)

            if map_text == 'bo3' or map_text == 'bo5':
                match_link = result.find('a', class_='a-reset').get('href')
                maps = check_match(match_link)
                for map in maps:
                    iag.probs[map.name][iag_pos] += calc_coefs_for_map(map.team1_score, map.team2_score, enemy_team_raiting, actual_coef)
                    print(map.name, map.team1_score + '-' + map.team2_score, calc_coefs_for_map(map.team1_score, map.team2_score, enemy_team_raiting, actual_coef))
            elif map_text in short_to_long_maps_names:
                map_name = short_to_long_maps_names[map_text]
                result_scre = result.find('td', class_='result-score').text
                team1_score = result_scre.split('-')[0].strip()
                team2_score = result_scre.split('-')[1].strip()

                iag.probs[map_name][iag_pos] += calc_coefs_for_map(team1_score, team2_score, enemy_team_raiting, actual_coef)
                print(map_name, team1_score + '-' + team2_score, calc_coefs_for_map(team1_score, team2_score, enemy_team_raiting, actual_coef))

def calc_coefs_for_map(team1_score, team2_score, enemy_team_raiting, actual_coef):
    raiting_coef = (250 - enemy_team_raiting) / 70

    team1_score = int(team1_score)
    team2_score = int(team2_score)
    if team1_score < 1: team1_score = 1
    if team2_score < 1: team2_score = 1

    reduce_coef = 5

    if team1_score > team2_score:
        return team1_score / team2_score * raiting_coef * actual_coef / reduce_coef + 1
    else:
        return -(team2_score / team1_score * raiting_coef * actual_coef / reduce_coef + 1)

def check_match(link):
    match_page = BeautifulSoup(Scraper.get_html('https://www.hltv.org/' + link), 'lxml')

    maps = []
    for map in match_page.find_all('div', class_='mapholder'):
        try:
            map_name = map.find('div', class_='mapname').text
            results = map.find('div', class_='results').text.split(' ')[0]
            team1_score = results.split(':')[0]
            team2_score = results.split(':')[1]
            maps.append(Map(map_name, team1_score, team2_score))
        except AttributeError:
            pass

    return maps

# returns an array of names of teams in the match
def get_names(soup):
	names=[]
	for name in soup.findAll('div', class_ ='teamName'):
		names.append(name.text)

	return names

if __name__ == "__main__":
	main()
