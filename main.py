from time import time
from bs4 import BeautifulSoup
from scraper import Scraper
from structs import InfoAboutGame, Map, GetTeamRaiting


def main():
    # link = str(input())
    link = 'https://www.hltv.org/matches/2332718/nemiga-vs-havu-vulkanbet-invitational'
    parse_match(link)

def parse_match(link):
    soup = BeautifulSoup(Scraper.get_html(link), 'lxml')

    iag = InfoAboutGame(get_names(soup)[0], get_names(soup)[1])

    check_last_games(soup, iag)

    # iag.probs['Cache'] = [50, 50]
    # iag.probs['Dust 2'] = [60, 40]
    # iag.probs['Mirage'] = [70, 30]
    # iag.probs['Inferno'] = [80, 20]
    # iag.probs['Nuke'] = [90, 10]
    # iag.probs['Train'] = [95, 10]
    # iag.probs['Overpass'] = [100, 0]
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
                    iag.probs[map.name][iag_pos] *= calc_coefs_for_map(map.team1_score, map.team2_score, enemy_team_raiting, actual_coef)
                    print(map.name, map.team1_score + '-' + map.team2_score, calc_coefs_for_map(map.team1_score, map.team2_score, enemy_team_raiting, actual_coef))
            elif map_text in short_to_long_maps_names:
                map_name = short_to_long_maps_names[map_text]
                result_scre = result.find('td', class_='result-score').text
                team1_score = result_scre.split('-')[0].strip()
                team2_score = result_scre.split('-')[1].strip()

                iag.probs[map_name][iag_pos] *= calc_coefs_for_map(team1_score, team2_score, enemy_team_raiting, actual_coef)
                print(map_name, team1_score + '-' + team2_score, calc_coefs_for_map(team1_score, team2_score, enemy_team_raiting, actual_coef))

def calc_coefs_for_map(team1_score, team2_score, enemy_team_raiting, actual_coef):
    raiting_coef = (300 - enemy_team_raiting) / 100

    team1_score = int(team1_score)
    team2_score = int(team2_score)
    if team1_score < 1: team1_score = 1
    if team2_score < 1: team2_score = 1

    game_coef = team1_score / team2_score

    return game_coef * raiting_coef * actual_coef / 100 + 1

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

def print_coefs(win_prob_team1, win_prob_team2):
    max_percent = 95

    team1_coef = 1 / (win_prob_team1 / max_percent)
    team2_coef = 1 / (win_prob_team2 / max_percent)

    format = '%4.2f'
    print(format % team1_coef, '|', format % team2_coef)

def get_num_of_maps(page_src):
    match_desc: str = page_src.find('div', class_='padding preformatted-text').text
    num_of_maps: str = match_desc[match_desc.find('Best of ') + 8:match_desc.find('Best of') + 9]
    return int(num_of_maps)

def head_to_head(page_src):
    first_team_head_to_head = 1
    second_team_head_to_head = 1

    head_to_head_content: str = page_src.find('div', class_='standard-box head-to-head-listing')
    results_table: str = head_to_head_content.find('table', class_='table')
    games: str = results_table.find_all('tr')
    for game in games:
        date = game.find('td', class_='date').text

        result = game.find('td', class_='result')
        first_team_score = result.find_all('span')[0].text
        second_team_score = result.find_all('span')[1].text

        map = game.find('div', class_='dynamic-map-name-full').text

        # print(date, map)
        # print(first_team_score, '-', second_team_score)
        first_team_head_to_head += int(first_team_score)
        second_team_head_to_head += int(second_team_score)

    return first_team_head_to_head, second_team_head_to_head

# returns an array of names of teams in the match
def get_names(soup):
	names=[]
	for name in soup.findAll('div', class_ ='teamName'):
		names.append(name.text)

	return names

#return an array of team ranks
def get_ranks(soup):
	ranks = []
	for link in get_teams_profile_links(soup):
		profile_soup = BeautifulSoup(Scraper.get_html(link), 'lxml')
		ranks.append(profile_soup.find('div', 'profile-team-stat').find('a').text)

	return ranks

#returns an array with the links on hltv profile of playing teams
def get_teams_profile_links(soup):
	links=[]
	team_info = soup.findAll('div', class_ ='team')
	for i in range(2): links.append('https://www.hltv.org' + str(team_info[i].find('a').get('href')))
	return links


if __name__ == "__main__":
	main()
