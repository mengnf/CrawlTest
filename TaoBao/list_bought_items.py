import datetime

import requests
from lxml import etree

from common import get_user_agent, get_cookie_taobao, get_taobao_header, write_to_json, write_to_excel


class TaobaoOrder(object):
    """
    淘宝订单类
    """

    # 初始化
    def __init__(self):
        self.url = 'https://buyertrade.taobao.com/trade/itemlist/list_bought_items.htm'
        self.header = get_taobao_header()

    # 获取响应数据
    def get_responses(self, url):
        response = requests.get(url, headers=self.header)
        return response.content

    # 解析数据并保存
    def parse_list(self, page_list_data):
        # 打开注释掉的内容
        page_list_data = page_list_data.decode('gbk').replace('<!--', '').replace('-->', '')
        print(page_list_data)
        # 转为html内容
        html = etree.HTML(page_list_data)

        order_list = html.xpath('//table[@class="bought-table-mod__table___AnaXt bought-wrapper-mod__table___3xFFM"]')
        print(html)
        print(order_list)
        if order_list:
            order_info_list = []
            for order_item in order_list:
                order_info = {}
                # 时间
                order_info['order_date'] = order_item.xpath('./*/span[@class="bought-wrapper-mod__create-time___yNWVS"]/text()')[0]
                # 订单号
                order_info['order_id'] = order_item.xpath('./*/td[@class="bought-wrapper-mod__head-info-cell___29cDO"]/span[1]/span[3]/text()')[0]
                # 金额
                order_info['order_amount'] = order_item.xpath('./*/div[@class="price-mod__price___3_8Zs"]/p//span[2]/text()')[0]
                # 状态
                order_info['order_status'] = order_item.xpath('./*/span[@class="text-mod__link___1rXmw"]/text()')[0]
                # 产品标题
                order_info['Product_title'] = order_item.xpath('./*/td[@class="sol-mod__no-br___36X3g"]/div[1]/div[2]/p[1]/a[1]/span[2]/text()')[0]
                # 产品链接
                order_info['Product_url'] = 'https:' + order_item.xpath('./*/td[@class="sol-mod__no-br___36X3g"]/div[1]/div[2]/p[1]/a[1]/@href')[0]

                order_info_list.append(order_info)
            print(order_info_list)

            write_to_json(order_info_list, f'淘宝订单_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}')
            write_to_excel(order_info_list, f'淘宝订单_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}')


    # 运行
    def run(self):
        # 下一页链接
        next_url = self.url
        print(next_url)
        # 获取页面数据
        page_list_data = self.get_responses(next_url)
        # print(page_list_data)
        # 解析列表数据并保存
        self.parse_list(page_list_data)

if __name__ == '__main__':
    taobaoOrer = TaobaoOrder()
    taobaoOrer.run()
