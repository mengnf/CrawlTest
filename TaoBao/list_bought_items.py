# -*-coding:utf-8-*-

import datetime
import json
import time

import requests

from common import get_user_agent, get_cookie_taobao, write_to_json, write_to_csv, write_to_excel
from settings import CrawlType


class TaoBaoOrder(object):
    """
    淘宝订单类
    """

    # 初始化
    def __init__(self):
        self.header = {'user-agent': get_user_agent(),
                       'referer': 'https://buyertrade.taobao.com/trade/itemlist/list_bought_items.htm'}

        self.cookies = get_cookie_taobao()
        self.dateBegin = int(time.mktime(time.strptime('2021-10-01 00:00:00', "%Y-%m-%d %H:%M:%S")) * 1000 + 441)
        self.dateEnd = int(time.mktime(time.strptime('2021-11-30 23:59:59', "%Y-%m-%d %H:%M:%S")) * 1000 + 441)
        self.totalPage = 1
        self.is_continue = True

    # 获取历史订单
    def get_history_order(self, pageNum, newURL=None):
        order_info_list = []

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
            order_info_list = self.parse_data(data.get('mainOrders'))
        else:
            self.is_continue = False
            print('没有数据了')

        return order_info_list

    # 解析数据
    def parse_data(self, data):
        order_info_list = []
        # 采集时间
        crawl_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # 采集类型
        crawl_type = CrawlType.REQUESTS

        if data:
            for order in data:
                if order:
                    tmp = {}
                    try:
                        # 订单ID
                        tmp['order_id'] = None
                        if 'id' in order:
                            tmp['order_id'] = order.get('id')
                        # 订单创建时间
                        tmp['order_create_datetime'] = None
                        if 'orderInfo' in order and order.get('orderInfo'):
                            if 'createTime' in order.get('orderInfo'):
                                tmp['order_create_datetime'] = order.get('orderInfo').get('createTime')
                        # 订单金额
                        tmp['order_amount'] = None
                        if 'payInfo' in order and order.get('payInfo'):
                            if 'actualFee' in order.get('payInfo'):
                                tmp['order_amount'] = order.get('payInfo').get('actualFee')
                        if 'statusInfo' in order and order.get('statusInfo'):
                            # 订单状态
                            tmp['order_status'] = None
                            if 'text' in order.get('statusInfo'):
                                tmp['order_status'] = order.get('statusInfo').get('text')
                            # 订单明细链接
                            tmp['order_detail_url'] = None
                            if 'url' in order.get('statusInfo'):
                                tmp['order_detail_url'] = 'https:' + order.get('statusInfo').get('url')
                        if 'subOrders' in order and order.get('subOrders'):
                            # 产品标题
                            tmp['title'] = None
                            if 'itemInfo' in order.get('subOrders')[0] and order.get('subOrders')[0].get('itemInfo'):
                                if 'title' in order.get('subOrders')[0].get('itemInfo'):
                                    tmp['title'] = order.get('subOrders')[0].get('itemInfo').get('title')
                            # 颜色分类，款式
                            tmp['skuText'] = None
                            if 'itemInfo' in order.get('subOrders')[0] and order.get('subOrders')[0].get('itemInfo'):
                                if 'skuText' in order.get('subOrders')[0].get('itemInfo') and order.get('subOrders')[0].get('itemInfo').get('skuText'):
                                    if 'value' in order.get('subOrders')[0].get('itemInfo').get('skuText')[0]:
                                        tmp['skuText'] = order.get('subOrders')[0].get('itemInfo').get('skuText')[0].get('value')
                            # 产品链接
                            tmp['url'] = None
                            if 'itemInfo' in order.get('subOrders')[0] and order.get('subOrders')[0].get('itemInfo'):
                                if 'itemUrl' in order.get('subOrders')[0].get('itemInfo'):
                                    tmp['url'] = 'https:' + order.get('subOrders')[0].get('itemInfo').get('itemUrl')
                        # 采集时间
                        tmp['crawl_datetime'] = crawl_datetime
                        # 采集类型
                        tmp['crawl_type'] = crawl_type

                        order_info_list.append(tmp)

                    except Exception as e:
                        print(f'解析出现异常：{e}')
                        continue

        return order_info_list

    def run(self):
        order_info_list = []

        i = 1
        while self.is_continue:
            print(f"正在抓取第{i}页...")
            order_info_list.extend(self.get_history_order(i))
            time.sleep(2)
            i += 1
        print(f"采集结束，共{len(order_info_list)}条")

        print('正在保存为json文件')
        # 保存到json文件
        write_to_json(order_info_list, f'淘宝订单_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}')

        print('正在保存为Excel文件')
        # 保存到Excel ↓↓↓
        # 列头排序
        sort = ['order_id', 'order_create_datetime', 'order_amount', 'order_status', 'order_detail_url', 'title', 'skuText', 'url', 'crawl_datetime', 'crawl_type']
        # 列头命名
        columns_map = {
            'order_id': '订单编号',
            'order_create_datetime': '订单创建时间',
            'order_amount': '订单金额',
            'order_status': '订单状态',
            'order_detail_url': '订单明细链接',
            'title': '商品标题',
            'skuText': '颜色分类',
            'url': '商品链接',
            'crawl_datetime': '采集时间',
            'crawl_type': '采集类型'
        }
        write_to_excel(order_info_list, f'淘宝订单_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}', columns_map, sort)


if __name__ == '__main__':
    taoBaoOrder = TaoBaoOrder()
    taoBaoOrder.run()
