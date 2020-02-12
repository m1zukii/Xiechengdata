import requests,time,random
from bs4 import BeautifulSoup as bs
import  pymysql,json
from urllib.parse import urlencode,quote
from pprint import  pprint
from random import  random
dbconfig = {
    'host':'localhost',
    'user':'asd123',
    'password':'asdzxc',
    'port':3306,
    'db':'xiecheng',
    'charset':'utf8',
    'cursorclass':pymysql.cursors.DictCursor
}
def getPage(url,flag=True):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        if flag:
            return response.text
        else: return response.json()
    return None
def getSceneAA(provincename):
    db = pymysql.connect(**dbconfig)
    cursor = db.cursor()
    scenes = []
    select = 'select * from aa where provincename = %s '
    try:
        cursor.execute(select, [provincename])
        datas = cursor.fetchall()
        for data in datas:
            scenes.append(data['name'])
        return scenes
    except Exception as e:
        print(e)
        return None
def getScene100(provincename):
    db = pymysql.connect(**dbconfig)
    cursor = db.cursor()
    scenes = []
    select = 'select * from scene100 where provincename = %s '
    try:
        cursor.execute(select, [provincename])
        datas = cursor.fetchall()
        for data in datas:
            scenes.append(data['name'])
        return scenes
    except Exception as e:
        print(e)
        return  None
def getCity(url,provincename):
    html = getPage(url)
    text = bs(html, 'lxml')
    # lis = text.select('#mainbar > div.leftbar > div:nth-child(8) > div > ul > li')
    lis = text.select('#mainbar > div.leftbar > div:nth-child(5) > div > ul > li')
    f = open('temp.txt','w',encoding='utf8')
    # f = open('city.txt','a',encoding='utf8')
    for li in lis:
        name = li.a['title']
        href = li.a['href']
        dict = {
            'name':name,
            'href':href,
            'province':provincename
        }
        f.write(json.dumps(dict,ensure_ascii=False)+'\n')
def getProvinceCity(provincename):
    f = open('city.txt','r',encoding='utf8')
    lines = f.readlines()[:]
    for line in lines:
        line = json.loads(line,encoding='utf8')
        if line['province'] != provincename:
            continue
        url = line['href']+'jingdian/'
        getScene(url,line['name'],provincename)
        second = random.random()+1.5
        time.sleep(second)
def getScene(url,areaname,provincename):
    html = getPage(url)
    if not html:return
    text = bs(html,'lxml')
    divs = text.select('div.w638-1')
    num = len(divs)
    scenes = []
    if num == 1:
        divs = divs[0]
        temp = divs.select('div ul li')
        if len(temp) == 0 : return
        for li in temp:
            a = li.a
            dict = {
                'name':a['title'],
                'href':a['href'],
                'provincename':provincename
            }
            scenes.append(dict)
    elif num == 2:
        divs = divs[0:2]
        for div in divs:
            for li in div.select('div ul li'):
                a = li.a
                dict = {
                    'name': a['title'],
                    'href': a['href'],
                    'provincename': provincename
                }
                scenes.append(dict)
    elif num == 3:
        temp = divs[0]
        for li in temp.select('div ul li'):
            a = li.a
            dict = {
                'name':a['title'],
                'href':a['href'],
                'provincename':provincename
            }
            scenes.append(dict)
        temp = divs[2]
        for div in temp.select('div div.lyts-title'):
            a = div.span.a
            href = a['href']
            second = random.random() + 0.5
            time.sleep(second)
            getScene(href,areaname,provincename)
    elif num == 4:
        divs = divs[0:4]
        for div in divs:
            for li in div.select('div ul li'):
                a = li.a
                dict = {
                    'name': a['title'],
                    'href': a['href'],
                    'provincename': provincename
                }
                scenes.append(dict)
        temp = divs[3]
        for div in temp.select('div div.lyts-title'):
            a = div.span.a
            href = a['href']
            second = random.random() + 0.5
            time.sleep(second)
            getScene(href, areaname,provincename)
    db = pymysql.connect(**dbconfig)
    cursor = db.cursor()
    insert = 'insert ignore into aa (name,href,provincename) values ( %s , %s , %s)'
    for data in scenes:
        try:
            cursor.execute(insert,tuple(data.values()))
            db.commit()
        except Exception as e:
            print(e)
            print('fail',areaname,data['name'])
        # print('success', areaname)
    cursor.close()
def getTags(name,provincename):
    db = pymysql.connect(**dbconfig)
    cursor = db.cursor()
    select = 'select href from aa where name = %s and provincename = %s'
    update = 'update scene100 set tags = %s where name = %s and provincename = %s'
    f = open('fail.txt','a',encoding='utf8')
    try:
        cursor.execute(select,[name,provincename])
        data = cursor.fetchone()
        href = data['href']
        if not len(href):
            print('href len',name)
            f.write(name+'\n')
            return
        if href[0:2] == '//':
            href = 'http:'+href
        html = getPage(href)
        text = bs(html,'lxml')
        tags = text.select('div#header div.dnew-bq a')
        if not len(tags): return
        a = []
        for tag in tags:
            a.append(tag.get_text().strip())
        temp = json.dumps(a,ensure_ascii=False)
        cursor.execute(update,[temp,name,provincename])
        db.commit()
        print('success',name,provincename)
    except Exception as e :
        print(e)
        print('fail',name,provincename)
    finally:
        f.close()
        cursor.close()
        db.close()
def getSame(provincename):
    db = pymysql.connect(**dbconfig)
    cursor = db.cursor()
    # selectall = 'select name from scene100 where provincename = %s'
    selectsame = 'select name from scene100 where name in ( select' \
             ' name from  aa where provincename = %s ) and ' \
             'provincename = %s '
    f = open('same.txt', 'w', encoding='utf8')
    try:
        # cursor.execute(selectall,[provincename])
        # all = cursor.fetchall()
        cursor.execute(selectsame,[provincename,provincename])
        same = cursor.fetchall()
        for s in same:
            name = s['name']
            f.write(name+'\n')
            # getTags(name,provincename)
            # time.sleep(random.random())
    except Exception as e:
        print(e)
    finally:
        f.close()
        cursor.close()
        db.close()
    # s1 = getSceneAA(provincename)
    # s2 = getScene100(provincename)
    # same = list(set(s2).intersection(set(s1)))
    # diff = list(set(s2).difference(set(s1)))
    # fs = open('ss/same.txt','w',encoding='utf8')
    # fd = open('ss/diff.txt','w',encoding='utf8')
    # for temp in same:
    #     fs.write(temp+'\n')
    # for temp in diff:
    #     fd.write(temp+'\n')
    # fs.close()
    # fd.close()
def readSame(provincename):
    f = open('same.txt','r',encoding='utf8')
    lines = f.readlines()
    for line in lines:
        getTags(line.strip(),provincename)
        time.sleep(random.random())
def search(name,sceneurl):
    db = pymysql.connect(**dbconfig)
    cursor = db.cursor()
    dict = {
        'kw':name,
        'type':0
    }
    temp = json.dumps(dict,ensure_ascii=False)
    url ='http://strip.elong.com/solr/index.html?req='+quote(temp)
    html = getPage(url,False)
    if not html:return
    a = html.get('destindex',{})
    if not a:
        print(1,end=' ')
        return
    res = html['destindex'][0]['url']
    baseurl = 'http://trip.elong.com/'
    update = 'update scene100 set tags = %s where name = %s and sceneurl = %s'
    try:
        html = getPage(baseurl+res)
        text = bs(html, 'lxml')
        tags = text.select('div#header div.dnew-bq a')
        if not len(tags): return
        a = []
        for tag in tags:
            a.append(tag.get_text().strip())
        if not a:
            print(1, end=' ')
        temp = json.dumps(a, ensure_ascii=False)
        cursor.execute(update, [temp, name, sceneurl])
        db.commit()
    except Exception as e:
        print(e)
        print('fail',name,sceneurl)
def readFile(left,right):
    f = open('tags.txt','r',encoding='utf8')
    lines = f.readlines()[left:right]
    for line in lines:
        dict = json.loads(line,encoding='utf8')
        name = dict['n']
        sceneurl = dict['u']
        search(name,sceneurl)
        seconds = random()
        time.sleep(seconds+1)
def getDesc():
    db = pymysql.connect(**dbconfig)
    cursor = db.cursor()
    select = 'select name,sceneurl from scene100  where tags IS NULL order by commentNum desc'
    f = open('tags.txt', 'w', encoding='utf8')
    try:
        cursor.execute(select)
        datas = cursor.fetchall()
        for data in datas:
            dict = {
                'n':data['name'],
                'u':data['sceneurl'],
            }
            f.write(json.dumps(dict, ensure_ascii=False) + '\n')
    except:
        pass
    finally:
        cursor.close()
    f.close()
if __name__ == '__main__':
    # str = '24.0006740000,121.59729'.split(',')
    # a,b = str[0][0:10],str[1]
    # print("'"+a+"' , '"+b+"' ")
    # readFile(800,860)
    # getDesc()
    # province = '海南'
    # getSame(province)
    # readSame(province)
    # name = '金水台温泉'
    # getTags(name,'广东')
    # getProvinceCity('陕西')
    # url = 'http://trip.elong.com/aomen/jingdian/'
    # areaname = '澳门'
    # getScene(url,areaname,areaname)
    # url = 'http://trip.elong.com/qingyuan/jingdian/'
    # getScene(url,1,2)
    # url = 'http://trip.elong.com/xinjiang/jingdian/'
    # provincename = '新疆'
    # getCity(url,provincename)
    # s1 = f()
    # s2 = ff()
    # a = list(set(s2).intersection(set(s1)))
    # b = list(set(s2).difference(set(s1)))
    # print(len(a),a)
    # print(len(b),b)
    # f = open('aaa.txt','w',encoding='utf8')
    # for bb in b:
    #     f.write(bb+'\n')
    # ff()
# print(len(scenes))
# print(len(scenes2))
# a = list(set(scenes2).intersection(set(scenes)))
# b = list(set(scenes2).difference(set(scenes)))
# print(len(a),a)
# print(len(b),b)
