import requests
from bs4 import BeautifulSoup
import re


def clear_mark(string):
    return re.sub(r'[，；。！？、]', '', string)


def reserve_search_poem(string):
    url = 'https://so.gushiwen.cn/search.aspx?value={}&valuej={}'.format(string, string[0])
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    data = soup.find('div', class_='sons')
    text = data.find('div', class_='contson')
    if not text:
        return None
    line = text.text
    line = clear_mark(line)
    # print(line)
    w = line.find(clear_mark(string))
    if w == -1:
        return None
    title = data.find('p').text
    title = re.sub(r'[\n\r ]', '', title)
    author = data.find('p', class_='source').text
    author = re.sub(r'[\n\r ]', '', author)
    return title, author


def search_poem(string):
    # url='http://www.esk365.com/sccx/scso.php?wd={}'.format(string)
    # r=requests.get(url)
    # soup = BeautifulSoup(r.text, 'html.parser')
    # data = soup.find('p',class_='z16 hl32 zq5')
    # l=[]
    # for i in data.children:
    #     l.append(i.string)
    # return l[0],l[1][1:-1]
    url = 'https://so.gushiwen.cn/search.aspx?value={}&type=mingju&valuej={}'.format(
        string, string[0])
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    # print (soup)
    data = soup.find('div', class_='sons')
    if not data:
        return reserve_search_poem(string)
    string = clear_mark(string)
    # print (data)
    line = data.find('a')
    # print (data)
    if (not line or clear_mark(line.text).find(string) == -1):
        # print (line.text,string, line.text.find(string))
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
