import requests
from bs4 import BeautifulSoup


def search_poem(string):
    # url='http://www.esk365.com/sccx/scso.php?wd={}'.format(string)
    # r=requests.get(url)
    # soup = BeautifulSoup(r.text, 'html.parser')
    # data = soup.find('p',class_='z16 hl32 zq5')
    # l=[]
    # for i in data.children:
    #     l.append(i.string)
    # return l[0],l[1][1:-1]
    url = 'https://so.gushiwen.cn/search.aspx?value={}&type=mingju'.format(
        string)
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    data = soup.find('div', class_='sons')
    if not data:
        return None
    # print (data)
    line = data.find('span')
    # print (data)
    if (not line or line.text != string):
        return None
    # line=line.parent.text
    # print(data.find_all('a')[1].text)
    author, title = data.find_all('a')[1].text.split('《')
    return title[:-1], author  # ,line


def get_poem():
    r = requests.get('https://v1.jinrishici.com/all.json')
    data = r.json()
    content = data['content']
    origin = data['origin']
    author = data['author']
    return content, origin, author


if __name__ == '__main__':
    print(search_poem(input()))
    print(get_poem())
