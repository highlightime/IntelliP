import requests

# URL에 HTTP GET 요청을 보냅니다.
response = requests.get('https://docs.minaprotocol.com/about-mina')

# 응답이 성공적이면 HTML 소스를 출력합니다.
if response.status_code == 200:
    html = response.text
    print(html)
else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")
