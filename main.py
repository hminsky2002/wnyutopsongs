import requests
from bs4 import BeautifulSoup

url = 'https://wnyu.org/admin/'
link = 'https://wnyu.org/admin/login'

##THIS WORKS WOOHOO
with requests.Session() as s:
    s.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36'
    r = s.get(url)
    soup = BeautifulSoup(r.text,"html.parser")
    payload = {i['name']:i.get('value','') for i in soup.select('input[name]')}
    payload['user[email]'] = 'Tech@wnyu.org'
    payload['user[password]'] = 'Radioradioradio89.1'
    res = s.post(link,data=payload)
    res = s.get(url)

    print(res.text)
