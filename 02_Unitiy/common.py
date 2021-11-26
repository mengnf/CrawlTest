# 公共方法类
# -*-coding:utf-8-*-
import datetime
import json
import os.path
import uuid
import xlwt
import pandas as pd


# 将数据保存为json文件
from settings import ATTACHMENT_PATH_JSON, ATTACHMENT_PATH_EXCEL


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
def write_to_excel(data, file_name):
    try:
        # 如果文件名没有值就默认赋值时间戳
        if not (file_name and file_name.strip()):
            file_name = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

        file_name = f'{ATTACHMENT_PATH_EXCEL}\{file_name}.xlsx'

        # 将字典列表转换为DataFrame
        pf = pd.DataFrame(list(data))
        # 指定字段顺序
        order = ['rank_num', 'rank_title', 'rank_url']
        pf = pf[order]
        # 将列名替换为中文
        columns_map = {
            'rank_num': '排名',
            'rank_title': '标题',
            'rank_url': '链接'
        }
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
        pass


# 获取去掉-的小写uuid字符串
def get_uuid():
    r_uuid = uuid.uuid1()
    return str(r_uuid).replace('-', '')
