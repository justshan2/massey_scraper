# Massey Data Scraper

A Python script that webscrapes ranking data from Massey ratings through Python requests and BeautifulSoup.

## Dependency Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install bs4 (BeautifulSoup).

```bash
pip install bs4
```

## Usage

_scraper.py_ is configured for current college football ratings. To change the sport / year of the ratings scraped, modify the following:

```bash
massey_base = 'https://masseyratings.com'
url = 'https://masseyratings.com/cf/fbs/ratings'
```

Changing url to the desired url will redirect the scraping target.

## License

[MIT](https://choosealicense.com/licenses/mit/)
