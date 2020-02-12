import requests
from bs4 import BeautifulSoup as bs
from pyquery import PyQuery as pq
import threading, time
from random import  random
import ast, os, json, pymysql
from pprint import pprint
from selenium import webdriver as wb
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
# 得到一个页面源代码
piaourl = 'https://piao.ctrip.com'
youurl = 'https://you.ctrip.com'
dbconfig = {
       'host': 'localhost',
       'user': 'asd123',
       'password': 'asdzxc',
       'port': 3306,
       'db': 'xiecheng',
       'charset': 'utf8',
       'cursorclass': pymysql.cursors.DictCursor
}
chrome_options = wb.ChromeOptions()
chrome_options.add_argument('--headless')
browser = wb.Chrome()
remove = ['可订明日','周末去哪','随买随用','暑假特惠','当地玩乐','可订今日'
            ,'自驾观赏','地铁直达','暑期特惠']
def getPage(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.75 Safari/537.36',
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        text = response.text
        actualurl = response.url
        return text, actualurl
    return None
def parseThumbnail(url,page,cityname,provincename):
    db = pymysql.connect(**dbconfig)
    cursor = db.cursor()
    html, actualurl = getPage(url)
    hotrank = (page-1)*15+1
    text = bs(html, 'lxml')
    divs = text.select('div.list_wide_mod2 div.list_mod2')
    baseurl = 'https://you.ctrip.com'
    insertStr = 'insert ignore into scene (name,sceneurl,address,commentNum,score,price,star,' \
                'hotrank,thumbimg,cityname,provincename) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    for div in divs:
        name = div.select('.rdetailbox dt a')[0].get_text()
        sceneurl = baseurl + div.select('.rdetailbox dt a')[0]['href']
        # dict,type = getSceneInfo(sceneurl)
        # time.sleep(2)
        thumbimg = div.select('.leftimg a img')[0]['src']
        span = div.select('.rdetailbox dd span.price')
        if len(span):
            price = span[0].get_text()
        else:
            price = ''
        address = div.select('.rdetailbox dd.ellipsis')[0].get_text().strip()
        temp = div.select('ul.r_comment li a.score strong')
        if len(temp):
            score = temp[0].get_text().strip()
        else:
            score = ''
        temp = div.select('ul.r_comment li a.recomment')[0].get_text().strip()
        if  temp.find('暂无点评') == -1 :
            commentNum = int(temp[1:-4])
        else : commentNum = 0
        span = div.select('.rdetailbox dl dd span.fenline')
        if len(span):
            star = span[0].previous_sibling.strip()
        else:
            star = ''
        scene = {
            'name': name,
            'sceneurl': sceneurl,
            'address': address,
            'commentNum': commentNum,
            'score': score,
            'price': price,
            'star': star,
            'hotrank':hotrank,
            'thumbimg':thumbimg,
            'cityname':cityname,
            'provincename':provincename
        }
        hotrank+=1
        try:
            cursor.execute(insertStr,tuple(scene.values()))
            print('success',cityname,page,end=' ')
            db.commit()
        except Exception as e:
            db.rollback()
            print(e)
            print('fail',cityname,page,end=' ')
    print('\n')
    db.close()
        # scene.update(dict)
        # insertStr1 = 'insert into scene (name,sceneurl,address,commentNum,score,price,star,hotrank,'\
        #     'imgUrl,time,tickets,feactures,traffic,cityname) values (%s,%s,%s,%s,%s,%s,'\
        #     '%s,%s,%s,%s,%s,%s,%s,'+cityname+')'
        # insertStr2 = 'insert into scene (name,sceneurl,address,commentNum,score,price,star,hotrank,' \
        #     'imgUrl,time,officialweb,feactures,phone,,cityname) values (%s,%s,%s'\
        #     ',%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'+cityname+')'
        # try:
        #     if type == 1:
        #         cursor.execute(insertStr1, tuple(scene))
        #     else:
        #         cursor.execute(insertStr2, tuple(scene))
        #     db.commit()
        # except :
        #     db.rollback()
    # db.close()
def getSceneInfo(url):
    chrome_options = wb.ChromeOptions()
    chrome_options.add_argument('--headless')
    browser = wb.Chrome(options=chrome_options)
    browser.get(url)
    # a = browser.find_elements_by_xpath('//*[@id="J-Ticket"]//a[@class="arrow_box" and contains(.,"展开")]')
    # for i in a:
    #     i.click()
    html = browser.page_source
    actualurl = browser.current_url
    text = bs(html, 'lxml')
    if actualurl.find(piaourl) != -1:
        imgs = text.select('.small_photo_wrap ul li')
        l = len(imgs)
        imgUrl = []
        if 10 <= l:
            imgs = imgs[0:10]
        elif 7 <= l < 10:
            imgs = imgs[0:7]
        elif 5 <= l < 6:
            imgs = imgs[0:5]
        else:
            imgs = imgs[0:l]
        for img in imgs:
            imgUrl.append(img.select('a img')[0]['src'])
        # address = text.select('.brief-right ul li span')[0].get_text()
        temp = text.select('.brief-right ul li.time span')
        time = temp[0].get_text().strip() if len(temp) else ''
        # tickets = []
        # doc = pq(html)
        # price = doc.find('td.td-price')
        # l = list(price.items())[0].text().strip()
        # if len(l):
        #     divs = doc.find('#J-Ticket>div:last-child .bml50')
        #     divs = list(divs.items())
        #     ld = len(divs)
        #     if ld >= 3:
        #         divs = divs[0:3]
        #     elif ld == 2:
        #         divs = divs[0:2]
        #     elif ld == 1:
        #         divs = divs[0]
        #     # print('ljr',len(divs))
        #     for div in divs:
        #         # print(div.html())
        #         title = div.find('span.tkt_type_title').text()
        #         siblings = div.next_all('div').items()
        #         for i in siblings:
        #             if not i.is_('.bml50'):
        #                 if i.find('tbody').not_('.tkt-bg-lightgray'):
        #                     name = i.find('.td-title').text().strip()
        #                     price = i.find('.td-price').text().strip()
        #                     tickets.append({
        #                             'name':title+name,
        #                             'price':price
        #                         })
        #             else:
        #                 break
        # else:
        #     divs = doc.find('#J-Ticket>div:last-child>div:not(.bml50)')
        #     divs = list(divs.items())
        #     ld = len(divs)
        #     if ld >= 3:
        #         divs = divs[0:3]
        #     elif ld == 2:
        #         divs = divs[0:2]
        #     elif ld == 1:
        #         divs = divs[0]
        #     else: divs = []
        #     for div in divs:
        #
        #         temp = div('td.td-title')
        #         # temp('span').remove()
        #         name = temp.text().strip()
        #         childrens = div.find('.tkt-bg-lightgray').items()
        #         for c in childrens:
        #             temp = c.find('.td2-1 a')
        #             temp('span').remove()
        #             n = temp.text().strip()
        #             p = c.find('.td5').text().strip()
        #             tickets.append({
        #                 'name': name+n,
        #                 'price': p
        #             })
        featureli = text.select('ul.introduce-feature li')
        features = []
        for i in featureli:
            features.append(i.select('span')[1].get_text().strip())
        temp = text.select('div.introduce-content')
        description = temp[0].get_text().strip()[0:600] if len(temp) else ''
        temp = text.select('.traffic-content')
        if len(temp):
            traffic = temp[0].get_text().strip()[4:]
        else : traffic = ''
        dict = {
            'imgUrl': json.dumps(imgUrl),
            'time': time,
            # 'tickets': json.dumps(tickets, ensure_ascii=False),
            'features': json.dumps(features, ensure_ascii=False),
            'traffic': traffic,
            'description':description
        }
        # print(dict,1)
        return dict,1
    else :
        features = []
        temp = text.select('.detailcon ul')
        if len(temp):
            features.append(temp[0].get_text().strip())
        temp = text.select('span.s_sight_con')
        if len(temp) == 2:
            phone = temp[0].get_text().strip()
            officialweb = temp[1].get_text().strip()
        elif len(temp)==1:
            phone = temp[0].get_text().strip()
            officialweb = ''
        else:
            phone = officialweb = ''
        temp = text.select('dl.s_sight_in_list dd')
        time = temp[0].get_text().strip() if len(temp)>0 else ''
        imgUrl = []
        imgs = text.select('.item a img')
        for i in imgs:
            imgUrl.append(i['src'])
        # trs = text.select('.play_table tr')
        # tickets = []
        # if len(trs)>1:
        #     for tr in trs[1:]:
        #         name = tr.select('td.one a')[0].get_text().strip()
        #         price = tr.select('td.three span.base_price')[0].get_text().strip()
        #         tickets.append({
        #             'name':name,
        #             'price':price
        #         })
        temp = text.select('div.toggle_l')
        description = temp[0].get_text().strip()[0:600] if len(temp) else ''
        dict = {
            'imgUrl': json.dumps(imgUrl),
            'time': time,
            'officialweb': officialweb,
            'features': json.dumps(features, ensure_ascii=False),
            'phone': phone,
            # 'tickets':json.dumps(tickets, ensure_ascii=False),
            'description':description
        }
        # print(dict,2)
        return dict,2
def getTotalPage(url):
    html = getPage(url)[0]
    text = bs(html,'lxml')
    total = text.select('b.numpage')
    if len(total):
        temp = total[0].get_text().strip()
        return int(temp)
    return 1
def getOneCityScene(cityurl,cityname):
    preurl = cityurl+'/p'
    afterurl = '.html'
    page = 1
    url = preurl + str(page) + afterurl
    total = getTotalPage(url)
    insertStr = ' insert ignore into city (img,name,href,presceneurl,recommend,province,hotrank)' \
                ' values (%s,%s,%s,%s,%s,%s,%s)'
    while page <= total:
        print('爬取',cityname,page)
        hotrank = (page-1)*10+1
        db = pymysql.connect(**dbconfig)
        cursor = db.cursor()
        html = getPage(preurl + str(page) + afterurl)[0]
        text = bs(html, 'lxml')
        citys = text.select('.list_mod1')
        baseurl = 'https://you.ctrip.com'
        scenelisturl = 'https://you.ctrip.com/sightlist'
        for i in citys:
            img = i.select('.cityimg a img')[0]['src']
            name = i.select('dl dt a')[0].get_text()
            temp = i.select('dl dt a')[0]['href'].strip()
            href = baseurl + temp
            index = temp.find('/place/') + 6
            presceneurl = scenelisturl + temp[index:-5] + '/s0-p'
            links = i.select('.ellipsis a')
            recommend = []
            for l in links:
                recommend.append(l.get_text().strip())
            dict = {
                'img': img,
                'name': name,
                'href': href,
                'presceneurl': presceneurl,
                'recommend': json.dumps(recommend, ensure_ascii=False),
                'province': cityname,
                'hotrank':hotrank
            }
            hotrank+=1
            try:
                cursor.execute(insertStr, tuple(dict.values()))
                db.commit()
            except Exception as e:
                db.rollback()
                print('error', e)
        page += 1
        second = random.random()+2
        time.sleep(second)
        db.close()
def getCityScene(preurl,cityname,provincename):
    print('爬取',provincename,cityname)
    afterurl = '.html?ordertype=11'
    page = 1
    url = preurl + str(page) + afterurl
    total = getTotalPage(url)
    if 55 <= total:
        last = 8
    elif 35 <= total < 55:
        last = 7
    elif 25 <= total < 35:
        last = 6
    elif 20 <= total < 25:
        last = 5
    elif 15 <= total < 20:
        last = 4
    elif 10 <= total < 15:
        last = 3
    elif 6 <= total < 10:
        last = 2
    else:
        last = 1
    while page <= last:
        parseThumbnail(preurl + str(page) + afterurl, page, cityname,provincename)
        page += 1
        second = random.random() + 2
        time.sleep(second)
def writetoFile(provincename):
    db = pymysql.connect(**dbconfig)
    cursor = db.cursor()
    province = [provincename]
    selectStr = 'select name,presceneurl from city where province = %s order by hotrank'
    f = open('relativetest.txt', 'w', encoding='utf8')
    try:
        cursor.execute(selectStr, tuple(province))
        datas = cursor.fetchall()
        for data in datas:
            f.write(json.dumps(data, ensure_ascii=False) + '\n')
    except Exception as e:
        print(e)
    f.close()
    db.close()
def readFromFile(provincename):
    f = open('relativetest.txt', 'r', encoding='utf8')
    lines = f.readlines()
    for line in lines:
        dict = json.loads(line, encoding='utf8')
        name = dict['name']
        preurl = dict['presceneurl']
        getCityScene(preurl, name, provincename=provincename)
        second = random.random() + 2
        time.sleep(second)
def write1(provincename,fail):
    select = 'select name,sceneurl from scene100 where provincename = %s'
    selectfail = 'select * from scene100 where imgUrl = "[]" '
    select1 = 'select * from scene100 where imgUrl is NULL or imgUrl = "[]" '
    db = pymysql.connect(**dbconfig)
    cursor = db.cursor()
    f = open('scene.txt', 'w', encoding='utf-8')
    province = [provincename]
    try:
        # if not fail:
        #     cursor.execute(select,province)
        # else:
        #     cursor.execute(selectfail,province)
        cursor.execute(select1)
        datas = cursor.fetchall()
        for data in datas:
            f.write(json.dumps(data, ensure_ascii=False) + '\n')
    except Exception as e:
        print(e)
    f.close()
    cursor.close()
def read1():
    f = open('scene.txt', 'r', encoding='utf8')
    update1 = 'update scene100 set imgUrl = %s ,time = %s ,' \
              'features = %s ,traffic = %s ,description = %s where name = %s and sceneurl = %s '
    update2 = 'update scene100 set imgUrl = %s ,time = %s ,officialweb = %s ,' \
              'features = %s ,phone = %s , description = %s ' \
              ' where name = %s and sceneurl = %s '
    start = time.time()
    db = pymysql.connect(**dbconfig)
    cursor = db.cursor()
    for line in f.readlines()[:]:
        line = json.loads(line, encoding='utf8')
        sceneurl = line['sceneurl']
        dict, type = getSceneInfo(sceneurl)
        dict['name'] = name = line['name']
        dict['sceneurl'] = sceneurl
        if type == 1:
           try:
               cursor.execute(update1,tuple(dict.values()))
               db.commit()
               print('success',name)
           except Exception as e:
               db.rollback()
               print(e)
               print('fail',name)
        elif type == 2:
            try:
                cursor.execute(update2, tuple(dict.values()))
                db.commit()
                print('success', name)
            except Exception as e:
                db.rollback()
                print(e)
                print('fail', name)
    db.close()
    end = time.time()
    print('时间', end - start)
def findTags(name,provincename,tags):
    # url2 = 'https://piao.ctrip.com/dest/u-view-spot/s-tickets/#ctm_ref=vat_hp_sb_lst'
    # url3 = 'https://piao.ctrip.com/dest/u-_ce_f7_b0_b2_b3_c7_c7_bd/s-tickets/#ctm_ref=vat_hp_sb_lst'
    wait = WebDriverWait(browser, 10)
    db = pymysql.connect(**dbconfig)
    cursor = db.cursor()
    url = 'https://piao.ctrip.com/dest'
    browser.get(url)
    update = 'update scene100 set tags = %s where name = %s and provincename = %s'
    try:
        input = browser.find_element_by_css_selector('input.main_search_txt')
        btn = browser.find_element_by_css_selector('a.main_search_btn')
        input.clear()
        input.send_keys(provincename+name)
        btn.click()
        html = browser.page_source
        text = bs(html,'lxml')
        scene = text.select('div.view-spot')
        if not len(scene):
            print('fail',name,provincename)
            return
        temp = scene[0].select('div.spot-label span.label')
        if not len(temp):return
        b = []
        for a in temp:
            tag = a.get_text().strip()
            if tag in remove:continue
            b.append(tag)
        if not len(b):return
        b = set(b)
        if not tags :
            before = set([])
        else:
            before = set(json.loads(tags,encoding='utf8'))
        after = before|b
        res = json.dumps(list(after),ensure_ascii=False)
        cursor.execute(update,[res,name,provincename])
        db.commit()
        print('success',name,provincename)
        # print(res)
        # print('before',before)
        print('add',b)
        # print('after',before|b)
    except Exception as e:
        print(e)
        print('fail',name,provincename)
        db.rollback()
    finally:
        cursor.close()
def getDesc():
    db = pymysql.connect(**dbconfig)
    cursor = db.cursor()
    select = 'select name,provincename,sceneurl,tags from scene100  order by commentNum desc'
    f = open('tags1.txt', 'w', encoding='utf8')
    try:
        cursor.execute(select)
        datas = cursor.fetchall()
        for data in datas:
            dict = {
                'n': data['name'],
                'p':data['provincename'],
                'u': data['sceneurl'],
                't':data['tags']
            }
            f.write(json.dumps(dict, ensure_ascii=False) + '\n')
    except:
        pass
    finally:
        cursor.close()
    f.close()
# def read(left,right):
#     f = open('tags1.txt', 'r', encoding='utf8')
#     lines = f.readlines()[left:right]
#     for line in lines:
#         dict = json.loads(line, encoding='utf8')
#         findTags(dict['n'], dict['p'], dict['t'])
#         seconds = random()
#         time.sleep(1 + seconds)
def getData():
    db = pymysql.connect(**dbconfig)
    cursor = db.cursor()
    sql = 'select name,sceneurl from scene100 where provincename = "北京" order by commentNum desc '
    f = open('bj.txt', 'w', encoding='utf8')
    try:
        cursor.execute(sql)
        datas = cursor.fetchall()
        for data in datas:
            url = data['sceneurl']
            left,right = url.rfind('/'),url.rfind('.html')
            dict = {
                'n':data['name'],
                'i':url[left+1:right],
                's': url
            }
            f.write(json.dumps(dict, ensure_ascii=False) + '\n')
    except:
        pass
    finally:
        cursor.close()
    f.close()
def read(left,right,flag):
    f = open('bj.txt','r',encoding='utf8')
    lines = f.readlines()[left:right]
    for line in lines:
        line = json.loads(line,encoding='utf8')
        name = line['n']
        sceneurl = line['s']
        id = line['i']
        getComment(url=sceneurl,scenename=name,id=id,flag=flag)
def getID():
    f = open('zj.txt','r',encoding='utf8')
    lines = f.readlines()
    array = []
    db = pymysql.connect(**dbconfig)
    cursor = db.cursor()
    update = 'update scenezj set id = %s where sceneurl = %s '
    for line in lines:
        line = json.loads(line,encoding='utf8')
        sceneurl = line['s']
        if youurl in sceneurl:
            left = sceneurl.rfind('/')+1
            right = sceneurl.rfind('.html')
            id = sceneurl[left:right]
            array.append(id)
        else:
            left = sceneurl.rfind('/dest/t') + 7
            right = sceneurl.rfind('.html')
            id = sceneurl[left:right]
            array.append(id)
        try:
            cursor.execute(update,[id,sceneurl])
            db.commit()
        except Exception as e :
            print(e)
    cursor.close()
    db.close()
    print(len(array))
    print(len(set(array)))
def getComment(url,scenename,id,flag):
    # print(scenename)
    browser.get(url)
    html = browser.page_source
    actualurl = browser.current_url
    text = bs(html, 'lxml')
    wait = WebDriverWait(browser, 10)
    baseurl = 'https://you.ctrip.com/'
    users = []
    dict = {}
    # 不可访问主页
    f1 = open('a.txt','a',encoding='utf8')
    print(actualurl)
    if actualurl.find(piaourl) != -1:
        total =  wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'a.btn-last-page'))).text
        # total = text.select('a.btn-last-page ')[0].get_text().strip()
        total = int(total)
        print(scenename,'total',total,'id',id)
        f1.write(scenename+str(total)+'\n')
        total = min(301, total)
        # total = min(350, total)
        for p in range(total):
            text = bs(browser.page_source,'lxml')
            comments = text.select('ul.comments li')
            print('page',p,len(comments),end=' ')
            for comment in comments:
                score = comment.h4.get_text().strip()[0]
                span = comment.div.span.get_text().strip().split()
                name , time1 = span[0],span[1]+'|'+span[2]
                dict.setdefault(name,{
                    's':score,
                    't':time1
                })
                users.append(name)
            next = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'ul.pkg_page a.down')))
            next.click()
            time.sleep(random()+0.5)
        a, b, c = len(dict), len(set(users)), len(users)
        print()
        print(a, b, c)
        f1.write(str(a) + ' ' + str(b) + ' ' + str(c) + '\n')
        f1.close()
        f = open('res' + str(flag) + '.txt', 'a', encoding='utf8')
        for temp in dict.keys():
            d = dict[temp]
            f.write(temp + ' ' + str(id) + ' ' + d['s'] + ' ' + d['t']+'\n')
        f.close()
        print('name',scenename,'total',total,'id',id)
    # 可访问主页
    else:
        total = text.select('div.pager_v1 b.numpage')[0].get_text().strip()
        total = int(total)
        print(scenename, 'total', total, 'id', id)
        f1.write(scenename+str(total)+'\n')
        total = min(300,total)
        for p in range(total):
            text = bs(browser.page_source, 'lxml')
            comments = text.select('div#sightcommentbox  div.comment_single')
            print('page', p, len(comments),end=' ')
            for comment in comments:
                name = comment.select('span.ellipsis')[0].get_text().strip()
                time1 = comment.select('span.time_line')[0].get_text().strip()
                score = comment.select('span.starlist span')[0]['style']
                homepage = baseurl + comment.select('span.ellipsis a')[0]['href']
                if '100' in score:
                    score = 5
                elif '80' in score:
                    score = 4
                elif '60' in score:
                    score = 3
                elif '40' in score:
                    score = 2
                elif '20' in score:
                    score = 1
                else:
                    score = 0
                dict.setdefault(name, {
                    's': score,
                    't': time1
                })
                users.append(name)
                # print(name,time1,score,homepage)
            # next = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.pager_v1 a.nextpage')))
            # next.click()
            try:
                input = wait.until(EC.presence_of_element_located((By.ID, 'gopagetext')))
                input.clear()
                input.send_keys(p + 1)
                btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.gopage')))
                btn.click()
            except Exception as e:
                print(e)
            time.sleep(random() + 1)
        a,b,c = len(dict),len(set(users)),len(users)
        print()
        print(a,b,c)
        f1.write(str(a)+' '+str(b)+' '+str(c)+'\n')
        f1.close()
        f = open('res'+str(flag)+'.txt', 'a', encoding='utf8')
        for temp in dict.keys():
            d = dict[temp]
            f.write(temp+' '+str(id)+' '+str(d['s'])+' '+d['t']+'\n')
        f.close()
        print('name',scenename,'total',total,'id',id)
if __name__ == '__main__':
    # getData()
    read(160,170,1)
    # url = 'http://www.baidu.com'
    # browser.get(url)
    # html = browser.page_source
    # print(html)
    # read(545,546,1)
    # read(370,380,2)
    # read(210,220,3)
    # read(58,59,1)
    # read(59,60,2)
    # read(60,61,3)
    # read(61,62,4)
    # read(62,63,5)
    # read(63,64,6)
    # getID()
    # url = 'https://you.ctrip.com/sight/hangzhou14/49894.html'
    # url = 'https://you.ctrip.com/sight/beijing1/64955.html'
    # getComment(url)
    # getData()
    # start = time.time()
    # read(6672,6673)
    # end = time.time()
    # print('time',end-start)
    # url = 'https://piao.ctrip.com/ticket/dest/t229.html'
    # getDesc()
    # name = '杭州长乔极地海洋公园'
    # findTags(name)
    # provincename = '宁夏'
    # write1(provincename=provincename,fail=True)
    # read1()
    # select = 'select provincename,count(*) from scene100 group by provincename order by count(*) desc'
    # db = pymysql.connect(**dbconfig)
    # cursor = db.cursor()
    # f = open('aa.txt', 'w', encoding='utf-8')
    # try:
    #     cursor.execute(select)
    #     datas = cursor.fetchall()
    #     for data in datas:
    #         f.write(json.dumps(data, ensure_ascii=False) + '\n')
    # except :
    #     pass
    # f.close()
    # cursor.close()
    # update1 = 'update scene123 set imgUrl = %s ,time = %s ,' \
    #           'features = %s ,traffic = %s ,description = %s where name = %s '
    # update2 = 'update scene123 set imgUrl = %s ,time = %s ,officialweb = %s ,' \
    #           'features = %s ,phone = %s , description = %s ' \
    #           ' where name = %s '
    # start = time.time()
    # f = open('beijing.txt','r',encoding='utf8')
    # lines = f.readlines()[14:17]
    # db = pymysql.connect(**dbconfig)
    # cursor = db.cursor()
    # for line in lines:
    #     line = json.loads(line,encoding='utf8')
    #     sceneurl = line['sceneurl']
    #     dict,type = getSceneInfo(sceneurl)
    #     dict['name'] = name = line['name']
    #     if type == 1:
    #        try:
    #            cursor.execute(update1,tuple(dict.values()))
    #            db.commit()
    #            print('success',name)
    #        except Exception as e:
    #            db.rollback()
    #            print(e)
    #            print('fail',name)
    #     elif type == 2:
    #         try:
    #             cursor.execute(update2, tuple(dict.values()))
    #             db.commit()
    #             print('success', name)
    #         except Exception as e:
    #             db.rollback()
    #             print(e)
    #             print('fail', name)
    #     second = random.random() + 2
    #     time.sleep(second)
    # db.close()
    # end = time.time()
    # print('时间',end-start)
    # provincename = '四川'
    # writetoFile(provincename=provincename)
    # readFromFile(provincename=provincename)
    # f = open('citys2.txt','r',encoding='utf8')
    # lines = f.readlines()
    # for line in lines:
    #     line = json.loads(line,encoding='utf8')
    #     name = line['name']
    #     cityurl = line['scenelisturl']
    #     getOneCityScene(cityurl,name)
    #     time.sleep(3.4)
    # url = 'https://you.ctrip.com/sitemap/spotdis/c0'
    # html = getPage(url)[0]
    # text = bs(html,'lxml')
    # div = text.select('.sitemap_block')[0]
    # lis = div.select('ul.map_linklist li')
    # baseurl = 'https://you.ctrip.com/countrysightlist/'
    # f = open('citys2.txt','a',encoding='utf8')
    # for li in lis:
    #     a = li.a
    #     name = a['title'][0:2]
    #     href = a['href']
    #     index = href.find('sight/')+6
    #     scenelisturl = baseurl + href[index:-5]
    #     dict = {
    #         'name':name,
    #         'scenelisturl':scenelisturl
    #     }
    #     f.write(json.dumps(dict,ensure_ascii=False)+'\n')
