import re
import xlwt
import requests
from bs4 import BeautifulSoup

def getHtml(url):
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        r.raise_for_status()
        r.encoding = "utf-8"
        return r.text
    except:
        print("Failed!!!")

def main():
    BASE_URL='https://www.kylc.com/stats/global/yearly/g_population_total/'

    year = 1959
    #创建数据集合
    listData = {}
    while year <=2018:
        url = BASE_URL+str(year)+'.html'
        html = getHtml(url)
        soup = BeautifulSoup(html, "html.parser")
        comment_list = soup.find('table', attrs={'class': 'table'}).find_all('tr')

        #增加数据列
        listData[str(year)] = []

        for j in comment_list[1:]:  # tr2[1:]遍历第1列到最后一列，表头为第0列
            td = j.find_all('td')  # td表格
            Rate = td[0].get_text().strip()  # 遍历排名
            Country = td[1].get_text().strip()  # 遍历国家
            Area = td[2].get_text().strip()  # 遍历洲
            Num = td[3].get_text().strip()  #遍历人数
            #正则匹配，提取数字
            tNum = "".join(re.findall(r".*\((.*)\)", Num)).replace(',','')
            #添加数据
            listData[str(year)].append([Rate, Country, Area, tNum])
        year+=1
    print (listData)  # 打印

    #读写excel（新建）
    workbook=xlwt.Workbook()
    sheet = workbook.add_sheet('ALLdata', cell_overwrite_ok=True)
    #设置列名
    row= ["年份","国家","洲","人数"]
    for i in range(0, len(row)):
        sheet.write(0, i, row[i])

    tmpcol=1#行
    for year in listData.keys():
        # 只输出前50个国家（可以改）
        for i in range(0, 50):
            sheet.write(tmpcol,0,str(year))
            for r in range(1, 4):
                sheet.write(tmpcol,r,listData[str(year)][i][r])
            tmpcol+=1
    #保存
    workbook.save('test.xls')

if __name__ == "__main__":
    main()
