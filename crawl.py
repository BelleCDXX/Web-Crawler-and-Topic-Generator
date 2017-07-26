from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


def get_page(siteURL):
	hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0',}

	req = Request(siteURL, headers=hdr)

	while True:
		try:
			page = urlopen(req)
			content = page.read()
			break
		except HTTPError as e:
			print(e.fp.read())
		except URLError as e:
			print (e.reason)
			 

	return content

