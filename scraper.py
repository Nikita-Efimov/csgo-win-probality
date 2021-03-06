from cfscrape import CloudflareScraper
from fake_useragent import UserAgent


class Scraper:
	scraper = CloudflareScraper()
	ua = UserAgent()
	personality = ua.random

	def get_html(url):
		request: CloudflareScraper

		for i in range(120):
			try:
				request = Scraper.scraper.get(url, headers={'User-Agent': Scraper.personality}, timeout=0.7)
				if request.status_code == 200:
					return request.content
				else:
					Scraper.personality = Scraper.ua.random
					continue
			except:
				pass

		print('Scraper can\'t do request')
		try:
			return request.content
		except:
			return ''
