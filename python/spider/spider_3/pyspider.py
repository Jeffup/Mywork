import re
import xlwt
import xlrd
import requests
from bs4 import BeautifulSoup
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib
import warnings
warnings.simplefilter('ignore', np.RankWarning)

def getHtml(url):
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        r.raise_for_status()
        r.encoding = "utf-8"
        return r.text
    except:
        print("Failed!!!")

def analyzeData(data,yearData,predictyear,proFig=False):
    '''
        data必须是dict_type。将生成预测数据和预测图样
        将预测5年的数据
    :param data:
    :param proFig: 是否生成图样
    :return:
    '''
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet('PREdata', cell_overwrite_ok=True)

    xdata = yearData
    baseyear = yearData[0]
    lastyear = yearData[-1]
    xdata1 = list(np.arange(lastyear+1, lastyear + predictyear+1))

    sheet.write(0, 0, '年份')
    tmpk=1
    for k in xdata1:
        sheet.write(tmpk, 0, str(k))
        tmpk+=1

    i=1
    for country in data.keys():
        #数据分析
        #拟合
        try:
            f1= np.polyfit(xdata, data[country], 3)
        except RankWarning:
            pass
        p1 = np.poly1d(f1)
        print(country,'人口数据拟合方程(3次) :\n', p1)
        #拟合
        yvals1 = p1(xdata)  # 拟合y值

        #预测
        yvals2 = p1(xdata1)
        sheet.write(0, i, country)
        for tmpk in range(1,predictyear+1):
            sheet.write(tmpk, i, str(yvals2[tmpk-1]))
        i+=1

        if(proFig):
            ln1 = plt.plot(xdata, data[country], color='red', label='original values')
            pln1 = plt.plot(xdata, yvals1, color='blue', linewidth=2.0, linestyle='-.', label='polyfit  values')
            # yvals1 = p1(xdata)  # 拟合y值
            plt.xlabel('year')
            plt.ylabel('population')
            plt.legend(loc=4)
            # plt.show()

            plt.savefig(country+".png")
            plt.close()
    workbook.save('preData.xls')

def writeXls(filename,data,yearData):
    '''
    写入数据到filename文件中
    :param filename: 文件名
    :param data: 数据列表
    :return:
    '''
    # 年份生成
    xdata = yearData
    baseyear = yearData[0]
    lastyear = yearData[-1]

    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet('ALLdata', cell_overwrite_ok=True)

    sheet.write(0, 0, '年份')
    tmpk=1
    for k in xdata:
        sheet.write(tmpk, 0, str(k))
        tmpk+=1

    i=1
    for key in data.keys():
        sheet.write(0, i, key)
        tmpk=1
        for value in data[key]:
            sheet.write(tmpk, i, str(value))
            tmpk+=1
        i+=1

    # 保存
    workbook.save(filename)

def readXls(filepath):
    '''
    读取数据
    :param filepath: 文件路径
    :return: 数据字典（内涵列表）+年份
    '''
    workbook= xlrd.open_workbook(filepath)
    listData={}
    yearData=[]
    #获取活跃表单
    worksheet=workbook.sheet_by_name('ALLdata')
    mrow=worksheet.nrows
    mcol=worksheet.ncols
    #获取年份
    tmpr=1
    tmpc=0
    while(tmpr<mrow):
        yearData.append(int(worksheet.cell(tmpr, 0).value))
        tmpr+=1
    tmpc+=1
    #获取数据
    while(tmpc<mcol):
        listData[worksheet.cell(0, tmpc).value]=[]
        tmpr=1
        while(tmpr<mrow):
            listData[worksheet.cell(0, tmpc).value].append(float(worksheet.cell(tmpr, tmpc).value))
            tmpr+=1
        tmpc+=1
    return [yearData,listData]

def spider():
    BASE_URL = 'https://www.kylc.com/stats/global/yearly/g_population_total/'

    baseyear = 1959
    year = baseyear
    lastyear = 1961
    yearData = list(np.arange(baseyear,lastyear+1))
    # 创建数据集合
    listData = {}
    while year <= lastyear:
        print('开始爬取第' + str(year) + '年的数据')
        url = BASE_URL + str(year) + '.html'
        html = getHtml(url)
        soup = BeautifulSoup(html, "html.parser")
        comment_list = soup.find('table', attrs={'class': 'table'}).find_all('tr')

        for j in comment_list[1:]:  # tr2[1:]遍历第1列到最后一列，表头为第0列
            td = j.find_all('td')  # td表格
            Rate = td[0].get_text().strip()  # 遍历排名
            Country = td[1].get_text().strip()  # 遍历国家
            Area = td[2].get_text().strip()  # 遍历洲
            Num = td[3].get_text().strip()  # 遍历人数
            # 正则匹配，提取数字
            tNum = "".join(re.findall(r".*\((.*)\)", Num)).replace(',', '')
            try:
                fNum = float(tNum)
            except ValueError:
                fNum = float(Num)
            # 添加数据
            if (Country not in listData.keys()):
                listData[Country] = []
            listData[Country].append(fNum)
        year += 1

    # 剔除年份不全的数据
    badkey = []
    for key in listData.keys():
        if (len(listData[key]) <= lastyear - baseyear):
            badkey.append(key)
    for key in badkey:
        listData.pop(key)
    return yearData,listData

def main():

    while True:
        choose = input('爬虫输入1，读取输入2:')
        if(choose=='1'):
            yearData,listData=spider()
            # 写入数据
            writeXls('spData.xls', listData, yearData)
            break
        elif(choose=='2'):
            try:
                yearData,listData=readXls('spData.xls')
            except FileNotFoundError:
                print('No such file ,please choose 1')
                continue
            break
        else:
            continue

    #进行数据分析
    analyzeData(listData,yearData,5,False)

if __name__ == "__main__":
    main()
