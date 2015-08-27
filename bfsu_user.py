import requests
import re
from bs4 import BeautifulSoup
import sqlite3

def get_true_name(username, password):
    '''
    Return the true name of a BFSU student to varify the identity. Or None.

    Directly use of this function is not good.
    username: a string of school id number
    password: a string of password used by user of Digital BFSU.
    '''
    try:
        login_page = requests.get('https://portal.bfsu.edu.cn')
        login_soup = BeautifulSoup(login_page.text, 'html.parser')
        post_data = {}
        for input in login_soup.find_all('input'):
            if input.get('name'):
                post_data[input.get('name')] = input.get('value', 'NULL')
        post_data['username'] = username
        post_data['password'] = password
        post_data['autoLogin'] = 'false'
        post_page = requests.post('https://cas.bfsu.edu.cn/cas/login', post_data)
        post_soup = BeautifulSoup(post_page.text, 'html.parser')
        skip_page = requests.get(post_soup.a['href'], cookies=post_page.cookies)
        skip2_page = requests.get('https://portal.bfsu.edu.cn/dcp/forward.action?path=/portal/portal&p=tradHomePage', cookies=post_page.cookies)
        skip2_soup = BeautifulSoup(skip2_page.text, 'html.parser')
        end_page = requests.get(skip2_soup.a['href'], cookies=skip2_page.cookies)
        return re.findall(r'edpinfo\.user\.user_name=\'(.+)\'', end_page.text)[0]
    except:
        return None

def get_user_info(openid):
    '''
    Return a tuple of (schoolid, name) if the openid given is registered in database. Or None.

    openid: string.
    '''
    co = sqlite3.connect('user.db')
    cu = co.cursor()
    cu.execute('select schoolid, name from user_info where openid=\'{}\';'.format(openid))
    info = cu.fetchone()
    cu.close()
    co.close()
    return info

def bind(openid, schoolid, password):
    '''
    Bind the wechat account with these infomation. Check if exists before run this.

    Return a tuple of (schoolid, name) if success. Or None. 
    openid: string.
    schoolid: string.
    password: string.
    '''
    name = get_true_name(schoolid, password)
    if not name:
        return None
    else:
        co = sqlite3.connect('user.db')
        cu = co.cursor()
        cu.execute('insert into user_info values(\'{}\', \'{}\', \'{}\');'.format(openid, schoolid, name))
        co.commit()
        cu.close()
        co.close()
        return (schoolid, name)

def unbind(openid):
    '''
    Unbind the account with its infomation. Check if exists before run this.

    openid: string.
    '''
    co = sqlite3.connect('user.db')
    cu = co.cursor()
    cu.execute('delete from user_info where openid=\'{}\';'.format(openid))
    co.commit()
    cu.close()
    co.close()

