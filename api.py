import requests
from bs4 import BeautifulSoup
import regex as re


def clear_mark(string):
    return re.sub(r'[，；。！？、]', '', string)


def mark_to_all(string):
    return re.sub(r'[，；。！？、]', '.?', string)


def judge(poem, inp):
    inp = mark_to_all(inp)
    inp = r'(?<=[；。！？]|^|\s)' + inp + r'(?=[；。！？]|$|\s)'
    res = re.search(inp, poem)
    if not res:
        return None
    line = res.group()
    if not line:
        return None
    if line[-1] not in ['。', '？', '！', '；']:
        line = line + poem[res.end():res.end() + 1]
    return line

def reserve_search_poem(string):
    url = 'https://so.gushiwen.cn/search.aspx?value={}&valuej={}'.format(string, string[0])
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    data = soup.find('div', class_='sons')
    if not data:
        return None
    text = data.find('div', class_='contson')
    if not text:
        return None
    line = text.text
    res = judge(line, string)
    if not res:
        return None
    title = data.find('p').text
    title = re.sub(r'[\n\r ]', '', title)
    author = data.find('p', class_='source').text
    author = re.sub(r'[\n\r ]', '', author)
    return title, author, res


def search_poem(string):
    url = 'https://so.gushiwen.cn/search.aspx?value={}&type=mingju&valuej={}'.format(
        string, string[0])
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    data = soup.find('div', class_='sons')
    if not data:
        return reserve_search_poem(string)
    line = data.find('a')
    if not line:
        return None
    res = judge(line.text, string)
    if not res:
        return None
    author, title = data.find_all('a')[1].text.split('《')
    return title[:-1], author, res


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
