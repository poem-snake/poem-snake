import requests
from bs4 import BeautifulSoup
import regex as re
from hashlib import md5


def clear_mark(string):
    return re.sub(r'[，；。！？、]', '', string)


def mark_to_all(string):
    return re.sub(r'[，；。！？、]', '[，；。！？、]?', string)


class Result:
    def __init__(self, error_type=1, title=None, author=None, content=None):
        self.title = title
        self.author = author
        self.content = content
        self.error_type = error_type

    def is_valid(self):
        return self.error_type == 1

    def error_msg(self):
        if self.error_type == 2:
            return "诗句不完全。"

    def __repr__(self):
        if not self.is_valid():
            return 'Error: {}'.format(self.error_type)
        return 'Title: {}\nAuthor: {}\nContent: {}'.format(self.title, self.author, self.content)


def judge(poem, inp):
    inp = r'.?'.join(list(inp))
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


def exjudge(poem, inp):
    poem = clear_mark(poem)
    inp = clear_mark(inp)
    w = poem.find(inp)
    if w == -1:
        return False
    return True


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
        if not exjudge(line, string):
            return None
        return Result(error_type=2)
    title = data.find('p').text
    title = re.sub(r'[\n\r ]', '', title)
    author = data.find('p', class_='source').text
    author = re.sub(r'[\n\r ]', '', author)
    return Result(title=title, author=author, content=res)


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
        if not exjudge(line.text, string):
            return None
        return Result(error_type=2)
    author, title = data.find_all('a')[1].text.split('《')
    return Result(title=title[:-1], author=author, content=res)


def gravatar(email):
    hash = md5(email.encode("utf-8")).hexdigest()
    return "https://gravatar.rotriw.com/avatar/{}?d=identicon".format(hash)


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
