# -*-coding:utf-8-*-
import datetime
import json
import random
import time

from lxml import etree
from selenium import webdriver
from selenium.webdriver import ActionChains

from common import write_to_json, write_to_excel, get_user_agent
from settings import TaoBaoText, CrawlType


class TaoBaoOrderDetail(object):
    """
    使用selenium获取淘宝订单明细
    """

    def __init__(self):
        self.url = 'https://login.taobao.com/'

    def xpath_exists(self, driver, xpath):
        try:
            driver.find_element_by_xpath(xpath)
            return True
        except:
            return False

    def get_order_detail(self):
        order_info_list = []

        print('使用selenium模拟登陆')
        # 使用selenium模拟登陆，获取并返回cookie
        username = TaoBaoText.USERNAME
        password = TaoBaoText.PASSWORD
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-blink-features=AutomationControlled')  # 去除浏览器selenium监控
        # options.add_argument('--headless')  # 浏览器不提供可视化页面
        options.add_argument('--disable-gpu')  # 禁用GPU加速
        # options.add_argument(get_user_agent())
        driver = webdriver.Chrome(options=options)
        driver.maximize_window()  # 窗口最大化
        # 访问指定的URL地址
        driver.get(self.url)

        driver.find_element_by_xpath('//*[@id="fm-login-id"]').send_keys(username)
        time.sleep(random.uniform(1.1, 3.1))  # 随机休息1.1秒到3.1秒之间
        driver.find_element_by_xpath('//*[@id="fm-login-password"]').send_keys(password)
        time.sleep(random.uniform(1.1, 3.1))  # 随机休息1.1秒到3.1秒之间
        driver.find_element_by_xpath('//*[@type="submit"]').click()  # 点击登录按钮
        time.sleep(random.uniform(1.1, 3.1))  # 随机休息1.1秒到3.1秒之间
        driver.find_element_by_id('bought').click()  # 点击已买到的宝贝
        time.sleep(random.uniform(1.1, 3.1))  # 随机休息1.1秒到3.1秒之间
        order_count = len(driver.find_elements_by_link_text('订单详情'))
        time.sleep(random.uniform(1.1, 3.1))  # 随机休息1.1秒到3.1秒之间
        if order_count > 0:
            for i in range(0, order_count):
                print(f'第{i+1}单')
                driver.switch_to.window(driver.window_handles[-1])  # 定位当前标签页
                driver.find_elements_by_link_text('订单详情')[i].click()  # 点击订单详情
                time.sleep(random.uniform(1.1, 3.1))  # 随机休息1.1秒到3.1秒之间
                driver.switch_to.window(driver.window_handles[-1])  # 定位当前标签页

                # 有滑块就一直滑
                while self.xpath_exists(driver, '//*[@id="nc_1_n1z"]'):
                    # 获取滑动按钮
                    btn_slide = driver.find_element_by_id('nc_1_n1z')
                    action = ActionChains(driver)
                    # 鼠标左键按下不放
                    action.click_and_hold(btn_slide).perform()
                    # 使用随机数确定滑动位置后滑动
                    action.drag_and_drop_by_offset(btn_slide, int(random.random() * 180) + 430, 0).perform()
                    time.sleep(random.uniform(1.1, 3.1))  # 随机休息1.1秒到3.1秒之间

                driver.switch_to.window(driver.window_handles[-1])  # 定位当前标签页
                time.sleep(random.uniform(1.1, 3.1))  # 随机休息1.1秒到3.1秒之间

                tmp = {}
                this_url = driver.current_url  # 获取当前页面链接
                print(this_url)
                if 'trade.taobao' in this_url:
                    print('淘宝订单')
                    # region 取出各字段的数据

                    # 订单状态
                    tmp['order_status'] = driver.find_element_by_xpath('//*[@id="detail-panel"]/div/div[2]/div/div[2]/div/div[1]/h3[1]').text

                    # 物流信息
                    # 发货方式
                    tmp['delivery_method'] = driver.find_element_by_xpath('//div[@class="logistics-info-mod__container___39ogG"]/table[1]//tr[1]/td/span[1]').text
                    # 物流公司
                    tmp['logistics_company'] = driver.find_element_by_xpath('//div[@class="logistics-info-mod__container___39ogG"]/table[1]//tr[2]/td').text
                    # 运单号码
                    tmp['waybill_number'] = driver.find_element_by_xpath('//div[@class="logistics-info-mod__container___39ogG"]/table[1]//tr[3]/td').text
                    # 物流跟踪
                    tmp['logistics_track'] = [
                        {
                            'datetime': item.find_element_by_xpath('./span[1]').text,
                            'progress': item.find_element_by_xpath('./span[2]').text
                        }
                        for item in driver.find_elements_by_xpath('//ul[@class="logistics-info-mod__list___2KLt8"]/li')
                    ]

                    # 订单信息
                    # 收货地址
                    tmp['receiv_address'] = driver.find_element_by_xpath('//dl[@class="address-memo-mod__an-box___y5ixN"][1]/dd[1]').text
                    # 卖家昵称
                    tmp['seller_nickname'] = driver.find_element_by_xpath('//div[@class="concat-info-mod__concat-info___oWpDv"]//tr[1]/td[1]/span[1]/span[1]').text
                    # 订单编号
                    tmp['order_id'] = driver.find_element_by_xpath('//*[@id="detail-panel"]/div/div[5]/div[2]/div/div/div/div[3]/div[1]/div[2]/span[1]/span[2]/span[1]').text
                    # 支付宝交易号
                    tmp['alipay_transaction_id'] = driver.find_element_by_xpath('//*[@id="detail-panel"]/div/div[5]/div[2]/div/div/div/div[3]/div[1]/div[2]/span[2]/span[2]/span[1]').text
                    # 创建时间
                    tmp['order_create_datetime'] = driver.find_element_by_xpath('//*[@id="detail-panel"]/div/div[5]/div[2]/div/div/div/div[3]/div[1]/div[2]/span[3]/span[2]/span[1]').text
                    # 付款时间
                    tmp['pay_time'] = driver.find_element_by_xpath('//*[@id="detail-panel"]/div/div[5]/div[2]/div/div/div/div[3]/div[1]/div[2]/span[4]/span[2]/span[1]').text
                    # 成交时间
                    tmp['deal_time'] = driver.find_element_by_xpath('//*[@id="detail-panel"]/div/div[5]/div[2]/div/div/div/div[3]/div[1]/div[2]/span[5]/span[2]/span[1]').text
                    # 商品信息
                    tmp['goods_info'] = [
                        {
                            'goods_title': item.find_element_by_xpath('./td[1]//div[@class="name"]/a[1]').text,  # 商品标题
                            'goods_url': item.find_element_by_xpath('./td[1]//div[@class="name"]/a[1]').get_attribute('href'),  # 商品链接
                            'goods_attribute': item.find_element_by_xpath('./td[2]').text,  # 商品属性
                            'goods_status': item.find_element_by_xpath('./td[3]').text,  # 商品状态
                            'unit_price': item.find_element_by_xpath('./td[5]').text,  # 单价
                            'goods_number': item.find_element_by_xpath('./td[6]').text,  # 商品数量
                        }
                        for item in driver.find_elements_by_xpath('//tr[@class="order-item"]')
                    ]
                    # 付款信息
                    tmp['pay_info'] = [
                        {
                            'name': item.find_element_by_xpath('./span[1]/span[1]').text,
                            'amount': item.find_element_by_xpath('./span[2]').text
                        }
                        for item in
                        driver.find_elements_by_xpath('//div[@class="pay-info-mod__get-money___2RJAu"]//ul[@class="pay-info-mod__fee-mess-list___1mKzy"]/li')
                    ]
                    tmp['pay_info'].append({
                        'name': driver.find_element_by_xpath('//div[@class="pay-info-mod__left___2m3nN"]/span[1]/span[1]').text,
                        'amount': driver.find_element_by_xpath('//div[@class="pay-info-mod__left___2m3nN"]/span[2]/strong').text
                    })

                    # endregion

                if 'trade.tmall' in this_url:
                    print('天猫订单')
                    # region 取出各字段的数据

                    # 订单状态
                    tmp['order_status'] = driver.find_element_by_xpath('//*[@id="J_trade_detail"]/div/dl/dd/span/h3').text

                    # 物流信息
                    # 发货方式
                    tmp['delivery_method'] = driver.find_element_by_xpath('//*[@id="J_trade_detail"]/div/ul/li/div/span[1]').text
                    # 物流公司
                    tmp['logistics_company'] = driver.find_element_by_xpath('//*[@id="J_trade_detail"]/div/ul/li/div/span[1]').text
                    # 运单号码
                    tmp['waybill_number'] = driver.find_element_by_xpath('//*[@id="J_trade_detail"]/div/ul/li/div/span[3]').text
                    # 物流跟踪
                    tmp['logistics_track'] = [
                        {
                            'datetime': item.find_element_by_xpath('./span[1]').text,  # 时间
                            'progress': item.find_element_by_xpath('./span[2]').text  # 进度
                        }
                        for item in driver.find_elements_by_xpath('//div[@class="package-detail-list drop-down-content"]//li[@class="status-done"]')
                    ]

                    # 订单信息
                    # 收货地址
                    tmp['receiv_address'] = driver.find_element_by_xpath('//*[@id="J_trade_imfor"]/div/ul/li[1]/div[2]/span').text
                    # 卖家昵称
                    tmp['seller_nickname'] = driver.find_element_by_xpath('//*[@id="J_trade_imfor"]/div/ul/li[4]/div[2]/span/span/span').text
                    # 订单编号
                    tmp['order_id'] = driver.find_element_by_xpath('//*[@id="J_trade_imfor"]/div/ul/li[3]/div[2]/span').text
                    # 交易信息
                    tmp['transaction_info'] = [
                        {
                            'name': item.find_element_by_xpath('./td[1]//span[1]').text,  # 名称：如支付宝交易号、付款时间、成交时间等
                            'value': item.find_element_by_xpath('./td[2]//span[1]').text  # 值
                        }
                        for item in driver.find_elements_by_xpath('//td[@id="J_trade_imfor"]//ul[1]/li[3]//table[@class="trade-dropdown-table"]//tr')
                    ]
                    # 商品信息
                    tmp['goods_info'] = [
                        {
                            'goods_title': item.find_element_by_xpath('.//div[@class="item-meta"]/a[1]').text,  # 商品标题
                            'goods_url': item.find_element_by_xpath('.//div[@class="item-meta"]/a[1]').get_attribute('href'),  # 商品链接
                            'goods_attribute': item.find_element_by_xpath('.//div[@class="item-meta"]/div').text,  # 商品属性
                            'unit_price': item.find_element_by_xpath('./td[@class="header-price font-high-light"]').text,  # 单价
                            'goods_number': item.find_element_by_xpath('./td[@class="header-count font-high-light"]').text,  # 商品数量
                            'goods_status': item.find_element_by_xpath('./td[@class="header-status"]').text  # 商品状态
                        }
                        for item in driver.find_elements_by_xpath('//li[@class="bought-listform-content"]/table//tr')
                    ]
                    # 付款信息
                    tmp['pay_info'] = [
                        {
                            'name': item.find_element_by_xpath('./span[1]').text,
                            'amount': item.find_element_by_xpath('./span[3]').text
                        }
                        for item in driver.find_elements_by_xpath('//table[@class="total-count-detail"]//span[@class="mixture"]/div/div')
                    ]

                    # endregion
                if tmp:
                    order_info_list.append(tmp)

                driver.close()  # 关闭当前标签页，如果只有一个标签页则关闭整个浏览器
                time.sleep(random.uniform(1.1, 3.1))  # 随机休息1.1秒到3.1秒之间

        return order_info_list

    def run(self):
        order_info_list = self.get_order_detail()
        print(f"采集结束，共{len(order_info_list)}条")

        print('正在保存为json文件')
        # 保存到json文件
        write_to_json(order_info_list, f'淘宝订单明细_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}')

        print('正在保存为Excel文件')
        # 保存到Excel ↓↓↓
        # 列头排序
        sort = ['order_status', 'delivery_method', 'logistics_company', 'waybill_number', 'logistics_track', 'receiv_address', 'seller_nickname', 'order_id', 'transaction_info', 'goods_info']
        # 列头命名
        columns_map = {
            'order_status': '订单状态',
            'delivery_method': '发货方式',
            'logistics_company': '物流公司',
            'waybill_number': '运单号码',
            'logistics_track': '物流跟踪',
            'receiv_address': '收货地址',
            'seller_nickname': '卖家昵称',
            'order_id': '订单编号',
            'transaction_info': '交易信息',
            'goods_info': '商品信息'
        }
        write_to_excel(order_info_list, f'淘宝订单明细_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}', columns_map, sort)


if __name__ == '__main__':
    taoBaoOrderDetail = TaoBaoOrderDetail()
    taoBaoOrderDetail.run()