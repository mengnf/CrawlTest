# -*- coding: utf-8 -*-
import csv
import datetime
import os.path

import requests
import re
import json
import time
from random import choice

from selenium import webdriver
from lxml import etree

from common import get_user_agent, get_cookie_taobao
from settings import ATTACHMENT_PATH_EXCEL, ATTACHMENT_PATH_EXCEL_TEST


class TaobaoOrder(object):

    def __init__(self):
        self.header = {'user-agent': get_user_agent(),
                       'referer': 'https://buyertrade.taobao.com/trade/itemlist/list_bought_items.htm'}

        self.cookies = get_cookie_taobao()
        self.dateBegin = int(time.mktime(time.strptime('2021-10-01 00:00:00', "%Y-%m-%d %H:%M:%S")) * 1000 + 441)
        self.dateEnd = int(time.mktime(time.strptime('2021-11-30 23:59:59', "%Y-%m-%d %H:%M:%S")) * 1000 + 441)
        self.totalPage = 1
        self.is_continue = True

    def getOnePageOrderHistory(self, pageNum, newURL=None):
        url = "https://buyertrade.taobao.com/trade/itemlist/asyncBought.htm"
        payload = {
            'action': 'itemlist/BoughtQueryAction',
            'event_submit_do_query': 1,
            '_input_charset': 'utf8'
        }
        formdata = {
            'dateBegin': self.dateBegin,
            'dateEnd': self.dateEnd,
            'pageNum': pageNum,
            'pageSize': 15,
            'prePageNo': pageNum - 1
        }

        # 验证码通过后，新的URL后面会带Token值
        # 带着这个值才能访问成功，并且访问下个页面不再需要验证码
        # newURL就是通过验证后的新URL
        if newURL:
            url = newURL

        try:
            response = requests.post(url, headers=self.header, params=payload, data=formdata, cookies=self.cookies)
            content = None

            if response.status_code == requests.codes.ok:
                content = response.text

        except Exception as e:
            self.is_continue = False
            print('出现异常：' + e)

        # 成功直接获取订单，失败进入验证码流程
        data = json.loads(content)
        # mainOrders有数据说明有订单数据
        if data.get('mainOrders'):
            self.getOrderDetails(data.get('mainOrders'))
        else:
            self.is_continue = False
            print('爬取结束')

    # 打印订单信息
    def getOrderDetails(self, data):
        crawl_datetime = datetime.datetime.now()
        for order in data:
            tmp = []
            companyName = ""
            mailNo = ""
            addr = "未知"
            name = ''
            phone = ''
            addr = ''
            if order.get('statusInfo').get('url') is not None:
                # 获取订单详情和快递号
                url = 'https:' + order.get('statusInfo').get('url')
                try:
                    response = requests.get(url, headers=self.header, cookies=self.cookies)

                    if 'tmall' in url:
                        # 天猫
                        # print(response.text)
                        element = etree.HTML(response.text)
                        div_list = element.xpath("//script[contains(text(),'detailData')]")[0].text.strip()[17:]
                        data = json.loads(div_list)
                        basic = data.get('basic').get('lists')[0].get('content')[0].get('text').split(',')
                        name = basic[0]
                        phone = basic[1].replace('86-', '')
                        addr = basic[2]
                        prompt = data.get('overStatus').get('prompt')
                        for p in prompt:
                            if p.get('key') == '物流':
                                companyName = p.get('content')[0].get('companyName')
                                mailNo = p.get('content')[0].get('mailNo')

                    else:
                        # 淘宝
                        # print(response.text)
                        element = etree.HTML(response.text)
                        info = element.xpath("//table[contains(@class, 'logistics-list')]")
                        if len(info) == 0:
                            # logistics - info - mod__container
                            div_list = element.xpath("//script[contains(text(),'JSON.parse')]")[0]. \
                                           text.strip()[23:-3]
                            data = json.loads(eval("'{}'".format(div_list)))
                            basic = data.get('deliveryInfo').get('address').split('，')
                            name = basic[0]
                            phone = basic[1].replace('86-', '')
                            addr = basic[2]
                            companyName = data.get('deliveryInfo').get('logisticsName')
                            mailNo = data.get('deliveryInfo').get('logisticsNum')



                        else:
                            div_list = info[0]
                            basic = div_list.xpath("//tbody/tr[3]/td[2]/text()")[-1].split('，')
                            if isinstance(basic, list):
                                name = basic[0].replace('\n', '').replace('\t', '').replace(' ', '')
                                phone = basic[1].replace('\n', '').replace('\t', '').replace(' ', '').replace('86-', '')
                                addr = basic[3].replace('\n', '').replace('\t', '').replace(' ', '')
                            companyName = div_list.xpath("//tbody/tr[5]/td[2]")[0].text.strip()
                            mailNo = div_list.xpath("//tbody/tr[6]/td[2]")[0].text.strip()
                    # if response.status_code == requests.codes.ok:
                    #     content = response.text

                except Exception as e:
                    pass
            # shopName
            tmp.append(order.get('id') + '\t')
            tmp.append(companyName)
            tmp.append(mailNo + '\t' if mailNo else '')
            tmp.append(name)
            tmp.append(phone + '\t' if phone else '')
            tmp.append(addr)
            tmp.append(order.get('seller').get('shopName'))
            # title
            tmp.append(order.get('subOrders')[0].get('itemInfo').get('title'))
            # createTime
            tmp.append(order.get('orderInfo').get('createTime'))
            # actualFee
            tmp.append(order.get('payInfo').get('actualFee'))
            # text
            tmp.append(order.get('statusInfo').get('text'))
            # 采集时间
            tmp.append(crawl_datetime)
            csv_write.writerow(tmp)

    def passCodeCheck(self, referer_url, pageNum):
        # 在url中插入style=mini获取包含后续要用到的所有参数的页面
        url = referer_url.replace("?", "?style=mini&")

        try:
            response = requests.post(url, headers=self.header, cookies=self.cookies)
            content = None

            if response.status_code == requests.codes.ok:
                content = response.text

        except Exception as e:
            pass

        # 获取identity, sessionid和type
        pattern = re.compile(
            'new Checkcode\({.*?identity: \'(.*?)\''
            '.*?sessionid: \'(.*?)\''
            '.*?type: \'(.*?)\'.*?}\)', re.S)
        data = pattern.findall(content)

        m_identity = data[0][0]
        m_sessionid = data[0][1]
        m_type = data[0][2]

        # 获取action, m_event_submit_do_unique, m_smPolicy
        # m_smApp, m_smReturn, m_smCharset, smTag
        # captcha和smSign
        pattern = re.compile(
            'data: {'
            '.*?action: \'(.*?)\''
            '.*?event_submit_do_unique: \'(.*?)\''
            '.*?smPolicy: \'(.*?)\''
            '.*?smApp: \'(.*?)\''
            '.*?smReturn: \'(.*?)\''
            '.*?smCharset: \'(.*?)\''
            '.*?smTag: \'(.*?)\''
            '.*?captcha: \'(.*?)\''
            '.*?smSign: \'(.*?)\',', re.S)
        data = pattern.findall(content)

        m_action = data[0][0]
        m_event_submit_do_unique = data[0][1]
        m_smPolicy = data[0][2]
        m_smApp = data[0][3]
        m_smReturn = data[0][4]
        m_smCharset = data[0][5]
        m_smTag = data[0][6]
        m_captcha = data[0][7]
        m_smSign = data[0][8]

        # 处理验证码
        res = False
        m_code = ""
        while res == False:
            res, m_code = self.checkCode(m_identity, m_sessionid, m_type, url)

        # 构建URL，获取最后的Token
        murl = "https://sec.taobao.com/query.htm"

        mheader = {}
        mheader['user-agent'] = self.choice(Configure.FakeUserAgents)
        mheader['referer'] = url

        mpayload = {
            'action': m_action,
            'event_submit_do_unique': m_event_submit_do_unique,
            'smPolicy': m_smPolicy,
            'smApp': m_smApp,
            'smReturn': m_smReturn,
            'smCharset': m_smCharset,
            'smTag': m_smTag,
            'captcha': m_captcha,
            'smSign': m_smSign,
            'ua': self.getUA(),  # 获取最新的UA
            'identity': m_identity,
            'code': m_code,
            '_ksTS': '{0:d}_39'.format(int(time.time() * 1000)),
            'callback': 'jsonp40'
        }

        try:
            response = requests.get(murl, headers=mheader, params=mpayload, cookies=self.cookies)
            content = None

            if response.status_code == requests.codes.ok:
                content = response.text

        except Exception as e:
            print(e)

        pattern = re.compile('{(.*?)}', re.S)
        data = pattern.findall(content)
        jsond = json.loads('{' + data[0] + '}')

        # 这个json文件里包含了最后访问用的URL
        murl = jsond.get('url')
        self.getOnePageOrderHistory(pageNum, murl)

    def checkCode(self, m_identity, m_sessionid, m_type, url):
        # 获取验证码的图片
        murl = "https://pin.aliyun.com/get_img"

        mheader = {}
        mheader['user-agent'] = choice(Configure.FakeUserAgents)
        mheader['referer'] = url

        mpayload = {
            'identity': m_identity,
            'sessionid': m_sessionid,
            'type': m_type,
            't': int(time.time() * 1000)
        }

        try:
            response = requests.get(murl, headers=mheader, params=mpayload, cookies=self.cookies)
            content = None

            if response.status_code == requests.codes.ok:
                content = response.content

        except Exception as e:
            print(e)

        # 将验证码图片写入本地
        with open("codeimg.jpg", "wb") as file:
            file.write(content)

        # 输入并验证验证码
        code = input("请输入验证码：")

        murl = "https://pin.aliyun.com/check_img"

        mpayload = {
            'identity': m_identity,
            'sessionid': m_sessionid,
            'type': m_type,
            'code': code,
            '_ksTS': '{0:d}_29'.format(int(time.time() * 1000)),
            'callback': 'jsonp30',
            'delflag': 0
        }

        try:
            response = requests.get(murl, headers=mheader, params=mpayload, cookies=self.cookies)
            content = None

            if response.status_code == requests.codes.ok:
                content = response.text

        except Exception as e:
            print(e)

        # 检测是否成功
        # 这里要返回这个验证码，后面会用到
        pattern = re.compile("SUCCESS", re.S)
        data = pattern.findall(content)

        if data:
            return True, code
        else:
            return False, code

    def getUA(self):
        # 利用PhantomJS模拟浏览器行为
        # 访问本地的js文件来获取UA
        driver = webdriver.PhantomJS()
        driver.get("D://taobao/ua.html")
        content = driver.find_element_by_tag_name('p').text
        driver.close()

        return content

    def getWuliu(self):
        url = 'https://trade.taobao.com/trade/detail/trade_order_detail.htm?biz_order_id=279823302640051289'
        try:
            response = requests.get(url, headers=self.header, cookies=self.cookies)

            if 'tmall' in url:
                # 天猫
                # print(response.text)
                element = etree.HTML(response.text)

                div_list = element.xpath("//script[contains(text(),'detailData')]")[0].text.strip()[17:]
                data = json.loads(div_list)
                basic = data.get('basic').get('lists')[0].get('content')[0].get('text').split(',')
                name = basic[0]
                phone = basic[1]
                addr = basic[2]
                prompt = data.get('overStatus').get('prompt')
                for p in prompt:
                    if p.get('key') == '物流':
                        companyName = p.get('content')[0].get('companyName')
                        mailNo = p.get('content')[0].get('mailNo')
                        print(companyName)


            else:
                # 淘宝
                # print(response.text)
                element = etree.HTML(response.text)
                info = element.xpath("//table[contains(@class, 'logistics-list')]")
                if len(info) == 0:
                    # logistics - info - mod__container
                    div_list = element.xpath("//script[contains(text(),'JSON.parse')]")[0]. \
                                   text.strip()[23:-3]
                    data = json.loads(eval("'{}'".format(div_list)))
                    basic = data.get('deliveryInfo').get('address').split('，')
                    name = basic[0]
                    phone = basic[1]
                    addr = basic[2]
                    companyName = data.get('deliveryInfo').get('logisticsName')
                    mailNo = data.get('deliveryInfo').get('logisticsNum')



                else:
                    div_list = info[0]
                    basic = div_list.xpath("//tbody/tr[3]/td[2]/text()")[-1].split('，')
                    if isinstance(basic, list):
                        name = basic[0].replace('\n', '').replace('\t', '').replace(' ', '')
                        phone = basic[1].replace('\n', '').replace('\t', '').replace(' ', '')
                        addr = basic[3].replace('\n', '').replace('\t', '').replace(' ', '')
                    companyName = div_list.xpath("//tbody/tr[5]/td[2]")[0].text.strip()
                    mailNo = div_list.xpath("//tbody/tr[6]/td[2]")[0].text.strip()
            # if response.status_code == requests.codes.ok:
            #     content = response.text

        except Exception as e:
            print(e)

    # 走起
    def run(self):
        i = 1
        while self.is_continue:
            print("正在抓取第{0:d}页,请稍后....".format(i))
            self.getOnePageOrderHistory(i)
            print("抓取第{0:d}页结束".format(i))
            time.sleep(2)
            i += 1


if __name__ == '__main__':
    # getWuliu()
    title = ["ID", "快递", "订单号", "姓名", "电话", "地址", "卖家", "名称", "订单创建时间", "价格", "状态", "采集时间"]
    file_name = f'{ATTACHMENT_PATH_EXCEL_TEST}\淘宝订单_{datetime.datetime.now().strftime("%Y%m%d")}.csv'
    if os.path.exists(file_name):
        out = open(file_name, 'a', newline='', encoding='utf-8-sig')
        csv_write = csv.writer(out, dialect='excel')
    else:
        out = open(file_name, 'a', newline='', encoding='utf-8-sig')
        csv_write = csv.writer(out, dialect='excel')
        csv_write.writerow(title)


    taobaoOrder = TaobaoOrder()
    taobaoOrder.run()
