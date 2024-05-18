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

def find_nth_occurrence(string, char, n):
    pos = -1
    for i in range(n):
        pos = string.find(char, pos + 1)
        if pos == -1:
            return -1
    return pos

def domain_filter(links, domain):
    same_domain_links = []
    for link in links:
        if domain in link:
            same_domain_links.append(link)
    return same_domain_links

def parse_depth_links(links, domain, depth):
    depth_parsed_links = []
    for link in links:
        # 1 depth 이상 링크는 1 depth로 제한
        if link.count('/') > (2+depth):
            # 3번째 / 이후로는 제거
            link_index = find_nth_occurrence(link, '/', 3+depth)
            link=link[:link_index]
            # 중복 링크 제거
        if link in depth_parsed_links:
            continue
        depth_parsed_links.append(link)
    return depth_parsed_links

def one_depth_fetch(links, domain, depth):
    print(f"Depth {depth}")
    parsed_links = parse_links(links, domain)
    https_links = append_https(parsed_links, domain)
    same_domain_links = domain_filter(https_links, domain)
    one_depth_links = parse_depth_links(same_domain_links, domain, depth)

    return one_depth_links

def main():
    total_links = []
    url = 'https://docs.minaprotocol.com'
    o=urlparse(url)
    domain=o.netloc
    links = get_page(url)
    one_depth_links = one_depth_fetch(links, domain, 1)
    total_links.append(one_depth_links)
    
    # one_depth_links에서 하나씩 링크 꺼내서 2 depth 링크 탐색
    for link in one_depth_links:
        links = get_page(link)
        two_depth_links = one_depth_fetch(links, domain, 2)
        total_links.append(two_depth_links)
        
    # two_depth_links 하나씩 링크 꺼내서 3 depth 링크 탐색
    for link in two_depth_links:
        links = get_page(link)
        three_depth_links = one_depth_fetch(links, domain, 3)
        total_links.append(three_depth_links)
    
    # 중복 링크 제거하고 flatten
    flattened_links = []
    for sublist in total_links:
        flattened_links.extend(sublist)
    flattened_links = list(set(flattened_links)) 
    
    # 줄바꿈해서 하나씩 출력
    for link in flattened_links:
        print(link)

if __name__ == '__main__':
    main()
