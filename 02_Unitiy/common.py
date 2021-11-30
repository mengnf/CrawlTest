# 公共方法类
# -*-coding:utf-8-*-
import csv
import datetime
import json
import os.path
import uuid
import random

import xlwt
import pandas as pd

from settings import ATTACHMENT_PATH_JSON, ATTACHMENT_PATH_EXCEL, USER_AGENT_LIST

import pymysql

import time
from selenium import webdriver


# 获取mysql配置连接
def get_mysql_connect():
    return pymysql.connect(host='192.168.2.104', port=3306, user='root', passwd='123456', db='CAREER', charset='utf8')


# 获取去掉-的小写uuid字符串
def get_uuid():
    r_uuid = uuid.uuid1()
    return str(r_uuid).replace('-', '')


# 随机获取user_agent
def get_user_agent():
    return random.choice(USER_AGENT_LIST)


# 获取淘宝cookie
def get_cookie_taobao():
    print('使用selenium模拟登陆')
    # 使用selenium模拟登陆，获取并返回cookie
    username = 'mengnf'
    password = 'Feige107358'
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    # options.add_argument('--headless')
    # options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)

    driver.get('https://login.taobao.com/')
    time.sleep(1)
    driver.find_element_by_xpath('//*[@id="fm-login-id"]').send_keys(username)
    time.sleep(1)
    driver.find_element_by_xpath('//*[@id="fm-login-password"]').send_keys(password)
    time.sleep(1)
    driver.find_element_by_xpath('//*[@type="submit"]').click()
    time.sleep(2)
    cookies_dict = {cookie['name']: cookie['value'] for cookie in driver.get_cookies()}
    driver.quit()
    return cookies_dict

# 获取淘宝header
def get_taobao_header():
    # cookie_str = ''
    # cookies_dict = get_cookie_taobao()
    # for cookie in cookies_dict:
    #     cookie_str += f'{cookie}={cookies_dict[cookie]};'

    header = {}
    header['user-agent'] = get_user_agent()

    return header

# 将数据保存为json文件
def write_to_json(data, file_name, en_ascii=True):
    try:
        # 判断是否有值
        if data:
            # 如果文件名没有值就默认赋值时间戳
            if not (file_name and file_name.strip()):
                file_name = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

            file_name = f'{ATTACHMENT_PATH_JSON}\{file_name}.json'
            print(file_name)

            # 序列化数据
            if en_ascii:
                json_data = json.dumps(data)
            else:
                json_data = json.dumps(data, ensure_ascii=False)

            # 将数据写入文件
            file = open(file_name, 'w')
            file.write(json_data)
            print('json文件保存成功')
    except Exception as ex:
        print(f'json文件保存失败：{ex}')


# 把二维列表存入excel中
def write_to_excel(data, file_name, columns_map=None, sort=None):
    try:
        # 如果文件名没有值就默认赋值时间戳
        if not (file_name and file_name.strip()):
            file_name = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

        file_name = f'{ATTACHMENT_PATH_EXCEL}\{file_name}.xlsx'

        # 将字典列表转换为DataFrame
        pf = pd.DataFrame(list(data))
        # 排序
        if sort:
            pf = pf[sort]
        # 列头重命名
        if columns_map:
            pf.rename(columns=columns_map, inplace=True)
        # 指定生成的Excel表格名称
        file_path = pd.ExcelWriter(file_name)
        # 替换空单元格
        pf.fillna('', inplace=True)
        # 输出
        pf.to_excel(file_path, encoding='utf-8', index=False)
        # 保存表格
        file_path.save()

        print('Excel文件保存成功')
    except Exception as ex:
        print(f'Excel文件保存失败：{ex}')


def write_to_csv(data, file_name):
    try:
        # 如果文件名没有值就默认赋值时间戳
        if not (file_name and file_name.strip()):
            file_name = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

        file_name = f'{ATTACHMENT_PATH_EXCEL}\{file_name}.csv'

        title = ["ID", "快递", "订单号", "姓名", "电话", "地址", "卖家", "名称", "订单创建时间", "价格", "状态", "采集时间"]

        out = open(file_name, 'w', newline='')
        csv_write = csv.writer(out, dialect='excel')
        csv_write.writerows(data.value)

        print('Excel文件保存成功')
    except Exception as ex:
        print(f'Excel文件保存失败：{ex}')
