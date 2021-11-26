# -*-coding:utf-8*-*
import datetime

import requests
from lxml import etree


from common import write_to_json, write_to_excel


class CrawlBilibiliRank(object):
    """
    B站排行爬虫
    """

    # 初始化类
    def __init__(self):
        self.url = 'https://www.bilibili.com/v/popular/rank/all'
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'
        }

    # 运行
    def run(self):
        # 下一页链接
        next_url = self.url
        print(next_url)
        # 获取页面数据
        page_list_data = self.get_data(next_url)
        # 解析列表数据并保存
        self.parse_list(page_list_data)

    # 获取网站响应内容
    def get_data(self, url):
        response = requests.get(url, headers=self.headers)
        return response.content

    def parse_list(self,page_list_data):
        # 打开注释掉的内容
        page_list_data = page_list_data.decode().replace('<!--', '').replace('-->', '')
        # 转为html内容
        html = etree.HTML(page_list_data)

        rank_data_list = html.xpath('//li[@class="rank-item"]')
        if rank_data_list:
            data_list = []
            for rank_item in rank_data_list:
                data_item = {}
                # 排名
                data_item['rank_num'] = rank_item.xpath('./div[@class="num"]/text()')[0]
                # 标题
                data_item['rank_title'] = rank_item.xpath('./*/div[@class="info"]/a/text()')[0]
                # 链接
                data_item['rank_url'] = 'https:' + rank_item.xpath('./*/div[@class="info"]/a/@href')[0]

                data_list.append(data_item)
            print(data_list)

            write_to_json(data_list, f'B站排行榜_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}')
            write_to_excel(data_list, f'B站排行榜_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}')


# 直接运行此类是__name__的值为__main__
if __name__ == '__main__':
    bilibili_rank = CrawlBilibiliRank()
    bilibili_rank.run()