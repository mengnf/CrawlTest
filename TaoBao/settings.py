# -*- coding:utf-8 -*-


def get_cookie():
    cookie_str = '_m_h5_tk=85a34dd4b54b8da0047138e31283e724_1637828525250; _m_h5_tk_enc=809358f69d1df138930bc009bc2791e6; cna=wHsNGrG0Lw4CAXd7e4I5xz2W; cookie2=154219bc0953035c91fb0bcd8858ae15; t=95b276fd1577c82d10a44b122f63a848; _tb_token_=35879eed3e78e; xlly_s=1; _samesite_flag_=true; sgcookie=E100vt43jkQ9+tyXb9OPXLu65Lfzp/K9KZAzgBQ2fT8XVcnVjyql4dXKljjVkb+JxS4+MZDM6MMs013nbmuuFbRe2mEEUm61BUk8X+O/wy7Rd+E=; unb=441517383; uc3=id2=Vyh9z0Bqr7Fy&nk2=DlVn2udp&vt3=F8dCvUj48zg2/WdkssU=&lg2=UIHiLt3xD8xYTw==; csg=c39de9e5; lgc=mengnf; cancelledSubSites=empty; cookie17=Vyh9z0Bqr7Fy; dnk=mengnf; skt=81272682ba6656ba; existShop=MTYzNzgyMTM3OQ==; uc4=nk4=0@DDC8hckxJ9J6aGPgg7C4fjA=&id4=0@VX9MjMqZYJhENbTyHUf5kFhHbFw=; publishItemObj=Ng==; tracknick=mengnf; _cc_=V32FPkk/hw==; _l_g_=Ug==; sg=f3b; _nk_=mengnf; cookie1=U+Nj4NIW2cLbvTTzqn3nfRDSo0Z5pionRhRgiDjEhSM=; ucn=center; v=0; mt=ci=7_1; uc1=cookie14=Uoe3cOXASb+s4Q==&existShop=false&cookie21=VFC/uZ9ajCbF8+YOUZmuyA==&cookie15=VT5L2FSpMGV7TQ==&cookie16=VFC/uZ9az08KUQ56dCrZDlbNdA==&pas=0; thw=cn; tfstk=cendB2qajCA3Shyt32LiVGjRL-9caBvL_9wd2daCL_YDfE61BsvKmmBCIeNUgWpO.; l=eBxDukyRg28sfOESBO5alurza779BIdb4sPzaNbMiInca1PPtF64zNCdKZneSdtjgtCv0etrRRzQkRLHR3fizbybTAJRKImIexvO.; isg=BO_vsNwy0vnivNbF2iGHoxhPfgP5lEO2nY8d9QF9fN5lUA9SCWfZBTVK0kDuKBsu'
    cookies = {data.split('=')[0]: data.split('=')[-1] for data in cookie_str.split(';')}

    print(cookies)
