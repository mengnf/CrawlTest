import time

from h2 import windows
from selenium import webdriver

from settings import TaoBaoText

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
driver.get('https://login.taobao.com/')

driver.find_element_by_xpath('//*[@id="fm-login-id"]').send_keys(username)
time.sleep(1)
driver.find_element_by_xpath('//*[@id="fm-login-password"]').send_keys(password)
time.sleep(1)
driver.find_element_by_xpath('//*[@type="submit"]').click()  # 点击登录按钮
time.sleep(1)
driver.find_element_by_id('bought').click()  # 点击已买到的宝贝
time.sleep(1)
order_count = len(driver.find_elements_by_link_text('订单详情'))
print(f'一共{order_count}单')
time.sleep(1)
if order_count > 0:
    for i in range(0, order_count):
        driver.find_elements_by_link_text('订单详情')[i].click()
        data_source = driver.page_source
        time.sleep(1)
time.sleep(10)
print('完成')