from bs4 import BeautifulSoup
from scraper import Scraper

def main():
    link = 'https://www.hltv.org/matches/2332740/intz-vs-singularity-esl-one-cologne-2019-north-america-open-qualifier-2'
    soup = BeautifulSoup(Scraper.get_html(link), 'lxml')

    match_desc: str = soup.find('div', class_='padding preformatted-text').text
    num_of_maps: str = match_desc[match_desc.find('Best of ') + 8:match_desc.find('Best of') + 9]
    print(num_of_maps)

if __name__ == "__main__":
	main()
