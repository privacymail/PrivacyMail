from bs4 import BeautifulSoup
import requests
from mailfetcher.models import Scanword


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
    name_words = Scanword.objects.filter(type__exact='name')
    link_words = Scanword.objects.filter(type__exact='link')

    found_urls = []

    for url in urls:
        if url.name:
            for word in name_words:
                if word.lower() in url.name.lower():
                    found_urls.append(url)
                    break
        if url.link:
            for word in link_words:
                if word.lower() in url.link.lower():
                    found_urls.append(url)
                    break
    found_urls = [url for url in found_urls if filter_blacklist_words(url)]

    return found_urls


def filter_blacklist_words(url):
    blacklist_words = Scanword.objects.filter(type__exact='blacklist')
    for word in blacklist_words:
        lower_word = word.lower()
        if url.name and lower_word in url.name.lower():
            return False
        if url.link and lower_word in url.link.lower():
            return False
    return True
