from bs4 import BeautifulSoup
from scraper import Scraper

def main():
    link = 'https://www.hltv.org/matches/2332740/intz-vs-singularity-esl-one-cologne-2019-north-america-open-qualifier-2'
    soup = BeautifulSoup(Scraper.get_html(link), 'lxml')

    match_desc: str = soup.find('div', class_='padding preformatted-text').text
    num_of_maps: str = match_desc[match_desc.find('Best of ') + 8:match_desc.find('Best of') + 9]

    print(get_names(soup))
    print(get_teams_profile_links(soup))
    print(get_ranks(soup))
    print(num_of_maps)


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
