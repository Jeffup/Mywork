import requests
from bs4 import BeautifulSoup
import time
import jieba
from PIL import Image
import numpy as np
import matplotlib.pyplot as plot

def getHtml(url):
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        r.raise_for_status()
        r.encoding = "utf-8"
        return r.text
    except:
        print("Failed!!!")

def getData(html,f):
    soup = BeautifulSoup(html, "html.parser")
    comment_list = soup.find('div', attrs={'class': 'mod-bd'})
    for comment in comment_list.find_all('div', attrs={'class': 'comment-item'}):
        comment_content = comment.find('span', attrs={'class': 'short'}).get_text()
        f.write(comment_content.encode('UTF-8'))


def seg_sentence(key):
    filepath1 = key + '评论.txt'
    filepath2 = key + '分析.txt'

    # 创建停用词列表
    filefath = 'stopwords.txt'
    stopwords = [line.strip() for line in open(filefath, 'r').readlines()]

    # 实现句子的分词
    final = ''
    fn1 = open(filepath1, 'r', encoding='utf-8').read()  # 加载爬取的内容
    sentence_seged = jieba.cut(fn1, cut_all=False)  # 结巴分词：精确模式
    fn2 = open(filepath2, "w", encoding='utf-8')

    #词典
    dict = {}

    for word in sentence_seged:
        if word not in stopwords:
            if word != '\t':
                if word not in dict.keys():
                    dict[word]=1
                else:
                    dict[word]+=1

    #取前50个高频词
    dict=sorted(dict.items(),key=lambda asd:asd[1],reverse=True)
    fn2.write(str(dict))
    fn2.close()

def main():

    moviename={'摔跤吧爸爸':'26387939','攀登者':'30413052','中国机长':'30295905'}

    for (key,value) in moviename.items():
        k = 0  # start = k
        i = 0
        filepath = key + '评论.txt'
        f = open(filepath, 'wb+')
        while k < 200:
            url = 'https://movie.douban.com/subject/'+value+'/comments?start=' + str(k) + '&limit=20&sort=new_score&status=P'
            k += 20
            i += 1
            print("正在爬取"+ key +"的第" + str(i) + "页的数据")
            time.sleep(2) # 设置睡眠时间
            html = getHtml(url)
            getData(html,f)
        f.close()
        seg_sentence(key)

if __name__ == "__main__":
    main()



