import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


def get_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    for link in soup.find_all('a'):
        links.append(link.get('href'))
    return links

def parse_links(links, domain):
    parsed_links = []
    for link in links:
        # #으로 시작하는 링크는 제외
        if link is not None and not link.startswith('#'):
            parsed_links.append(link)
    return parsed_links

def append_https(links, domain):
    https_links = []
    for link in links:
        if link.startswith('http'):
            https_links.append(link)
        else:
            # 현재 탐색하고 있는 페이지의 도메인을 앞에 붙여줌
            https_links.append("https://"+domain+link)
    return https_links

def domain_filter(links, domain):
    same_domain_links = []
    for link in links:
        if domain in link:
            same_domain_links.append(link)
    return same_domain_links

def main():
    url = 'https://docs.minaprotocol.com/about-mina'
    o=urlparse(url)
    domain=o.netloc
    links = get_page(url)
    parsed_links = parse_links(links, domain)
    https_links = append_https(parsed_links, domain)
    same_domain_links = domain_filter(https_links, domain)
    print(same_domain_links)

if __name__ == '__main__':
    main()
