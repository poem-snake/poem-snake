import requests
from bs4 import BeautifulSoup
def search_poem (string):
    # url='http://www.esk365.com/sccx/scso.php?wd={}'.format(string)
    # r=requests.get(url)
    # soup = BeautifulSoup(r.text, 'html.parser')
    # data = soup.find('p',class_='z16 hl32 zq5')
    # l=[]
    # for i in data.children:
    #     l.append(i.string)
    # return l[0],l[1][1:-1]
    url='https://so.gushiwen.cn/search.aspx?value={}'.format(string)
    r=requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    data = soup.find('div',class_='sons')
    # print (data)
    line = data.find('span',style='color:#B00815')
    if (not line):
        return None
    # line=line.parent.text
    title=data.find('p').text.replace('\n','')
    author=data.find('p',class_='source').text.replace('\n','')
    return title,author#,line

if __name__ == '__main__':
    print(search_poem(input()))