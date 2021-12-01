# -*-coding:utf-8-*-
import datetime
import json
import time

from lxml import etree
from selenium import webdriver

from common import write_to_json, write_to_excel
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
        # 创建一个浏览器对象
        driver = webdriver.Chrome()
        # 使用selenium模拟登陆，获取并返回cookie
        username = TaoBaoText.USERNAME
        password = TaoBaoText.PASSWORD
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-blink-features=AutomationControlled')  # 去除浏览器selenium监控
        # options.add_argument('--headless')  # 浏览器不提供可视化页面
        options.add_argument('--disable-gpu')  # 禁用GPU加速
        driver = webdriver.Chrome(options=options)

        # 访问指定的URL地址
        driver.get(self.url)

        driver.find_element_by_xpath('//*[@id="fm-login-id"]').send_keys(username)
        time.sleep(1)
        driver.find_element_by_xpath('//*[@id="fm-login-password"]').send_keys(password)
        time.sleep(1)
        driver.find_element_by_xpath('//*[@type="submit"]').click()  # 点击登录按钮
        time.sleep(1)
        driver.find_element_by_id('bought').click()  # 点击已买到的宝贝
        time.sleep(1)
        order_count = len(driver.find_elements_by_link_text('订单详情'))
        time.sleep(1)
        if order_count > 0:
            for i in range(0, order_count):
                print(f'第{i}单')
                driver.switch_to.window(driver.window_handles[-1])  # 定位当前标签页
                tmp = {}

                driver.find_elements_by_link_text('订单详情')[i].click()
                time.sleep(2)
                driver.switch_to.window(driver.window_handles[-1])  # 定位当前标签页

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
                tmp['logistics_track'] = [{'datetime': item.find_element_by_xpath('./span[1]').text, 'progress': item.find_element_by_xpath('./span[2]').text} for item in driver.find_elements_by_xpath('//div[@class="logistics-info-mod__container___39ogG"]/table[1]//tr[4]/td[1]/ul[1]/li')]

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
                # 商品标题
                tmp['goods_title'] = driver.find_element_by_xpath('//*[@id="detail-panel"]/div/div[5]/div[2]/div/div/div/div[3]/div[2]/table/tbody/tr[2]/td[1]/div[2]/div/div[1]/a[1]').text
                # 商品属性
                tmp['goods_attribute'] = driver.find_element_by_xpath('//*[@id="detail-panel"]/div/div[5]/div[2]/div/div/div/div[3]/div[2]/table/tbody/tr[2]/td[2]/div/span/span[2]/span[1]').text
                # 物流状态
                tmp['logistics_status'] = driver.find_element_by_xpath('//*[@id="detail-panel"]/div/div[5]/div[2]/div/div/div/div[3]/div[2]/table/tbody/tr[2]/td[3]/div/span[1]').text
                # 单价
                tmp['unit_price'] = driver.find_element_by_xpath('//*[@id="detail-panel"]/div/div[5]/div[2]/div/div/div/div[3]/div[2]/table/tbody/tr[2]/td[5]/span[1]').text
                # 商品数量
                tmp['goods_number'] = driver.find_element_by_xpath('//*[@id="detail-panel"]/div/div[5]/div[2]/div/div/div/div[3]/div[2]/table/tbody/tr[2]/td[6]').text
                # 订单金额
                tmp['order_amount'] = driver.find_element_by_xpath('//*[@id="detail-panel"]/div/div[5]/div[2]/div/div/div/div[4]/div[3]/div[2]/div/ul/li[1]/span[2]').text
                # 运费
                tmp['freight'] = driver.find_element_by_xpath('//*[@id="detail-panel"]/div/div[5]/div[2]/div/div/div/div[4]/div[3]/div[2]/div/ul/li[2]/span[2]').text
                # 优惠金额
                tmp['discount_amount'] = None
                if self.xpath_exists(driver, '//*[@id="detail-panel"]/div/div[5]/div[2]/div/div/div/div[4]/div[3]/div[2]/div/ul/li[3]/span[2]'):
                    tmp['discount_amount'] = driver.find_element_by_xpath('//*[@id="detail-panel"]/div/div[5]/div[2]/div/div/div/div[4]/div[3]/div[2]/div/ul/li[3]/span[2]').text
                # 实付金额
                tmp['pay_amount'] = driver.find_element_by_xpath('//*[@id="detail-panel"]/div/div[5]/div[2]/div/div/div/div[4]/div[3]/div[3]/div[1]/div[2]/span[2]/strong[1]').text

                order_info_list.append(tmp)

                print(order_info_list)
                driver.close()  # 关闭当前标签页，如果只有一个标签页则关闭整个浏览器
                time.sleep(1)
                
        time.sleep(1)
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
        sort = ['order_status', 'delivery_method', 'logistics_company', 'waybill_number', 'logistics_track', 'receiv_address', 'seller_nickname', 'order_id', 'alipay_transaction_id', 'order_create_datetime', 'pay_time', 'deal_time', 'goods_title', 'goods_attribute', 'order_status', 'logistics_status', 'goods_number', 'order_amount', 'freight', 'discount_amount', 'pay_amount']
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
            'alipay_transaction_id': '支付宝交易号',
            'order_create_datetime': '创建时间',
            'pay_time': '付款时间',
            'deal_time': '成交时间',
            'goods_title': '商品标题',
            'goods_attribute': '商品属性',
            'logistics_status': '物流状态',
            'unit_price': '单价',
            'goods_number': '商品数量',
            'order_amount': '订单金额',
            'freight': '运费',
            'discount_amount': '优惠金额',
            'pay_amount': '实付金额'
        }
        write_to_excel(order_info_list, f'淘宝订单明细_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}', columns_map, sort)


if __name__ == '__main__':
    taoBaoOrderDetail = TaoBaoOrderDetail()
    taoBaoOrderDetail.run()