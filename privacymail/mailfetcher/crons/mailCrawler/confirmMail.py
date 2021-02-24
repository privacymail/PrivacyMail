from bs4 import BeautifulSoup
import requests

SIGN_UP_WORDS = [
    'weiter', 'registrier', 'Anmeldung', 'klicke', 'Anmelden', 'bestätig',
    'hier', 'confirm', 'subscribe', 'register'
]
SIGN_UP_URL = ['subscribe']
BLACKLIST = ['unsubscribe', 'abmeldung', 'abmelden']


class URL:
    def __str__(self):
        if self.name and self.link:
            return f'{self.name}: {self.link}'
        elif self.name:
            return f'{self.name}: No URL'
        elif self.link:
            return f'No Name: {self.link}'
        else:
            return 'URL without link or name'

    def __init__(self, link, name):
        self.link = link
        self.name = name


def approve_from_mail(mail):
    '''
    Try to approve identity by mail
    '''
    urls = get_urls(mail.body_html)
    urls = filter_urls(urls)
    if len(urls) > 0:
        for url in urls:
            try:
                response = requests.get(url.link)
            except requests.exceptions.Timeout:
                print(f'Timed out trying to access {url.link} with name {url.name}')
                continue

            if response.status_code == 200:
                return True

    return False


def get_urls(html):
    '''
    Get all URLs from a html text.
    '''
    soup = BeautifulSoup(html, 'html.parser')
    urls = [URL(url.get('href'), url.string) for url in soup.find_all('a')]
    return urls


def filter_urls(urls):
    '''
    Filter list of URLs for keywords
    '''
    found_urls = []

    for url in urls:
        if url.name:
            for word in SIGN_UP_WORDS:
                if word.lower() in url.name.lower():
                    found_urls.append(url)
                    break
        if url.link:
            for word in SIGN_UP_URL:
                if word.lower() in url.link.lower():
                    found_urls.append(url)
                    break
    found_urls = [url for url in found_urls if filter_blacklist_words(url)]

    return found_urls


def filter_blacklist_words(url):
    for word in BLACKLIST:
        lower_word = word.lower()
        if url.name and lower_word in url.name.lower():
            return False
        if url.link and lower_word in url.link.lower():
            return False
    return True
