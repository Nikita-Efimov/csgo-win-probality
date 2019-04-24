from bs4 import BeautifulSoup
from scraper import Scraper


def get_num_of_maps(page_src):
    match_desc: str = page_src.find('div', class_='padding preformatted-text').text
    num_of_maps: str = match_desc[match_desc.find('Best of ') + 8:match_desc.find('Best of') + 9]
    return int(num_of_maps)

def head_to_head(page_src):
    first_team_head_to_head = 0
    second_team_head_to_head = 0

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

def print_coefs(win_prob_team1):
    team1_coef = 1 / (win_prob_team1 / 100)
    team2_coef = 1 / ((100 - win_prob_team1) / 100)

    format = '%.2f'
    print(format % team1_coef, format % team2_coef)

def parse_match(link):
    win_prob_team1 = 50

    soup = BeautifulSoup(Scraper.get_html(link), 'lxml')

    map_num_prob: float = (0, 0.99, 1, 1.01, 1.015, 1.02)[get_num_of_maps(soup)]

    first_team_head_to_head, second_team_head_to_head = head_to_head(soup)

    win_prob_team1 *= map_num_prob
    win_prob_team1 *= (first_team_head_to_head / second_team_head_to_head)

    print_coefs(win_prob_team1)

def main():
    link = 'https://www.hltv.org/matches/2332372/isurus-vs-detona-esl-pro-league-season-9-americas'
    parse_match(link)

if __name__ == "__main__":
	main()
