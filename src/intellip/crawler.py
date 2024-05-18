import requests
from bs4 import BeautifulSoup

def get_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    for link in soup.find_all('a'):
        links.append(link.get('href'))
    return links

def main():
    url = 'https://docs.minaprotocol.com/about-mina'
    links = get_page(url)
    print(links)

if __name__ == '__main__':
    main()
