import queue
import datetime
import threading
import random,time
import requests
import re
import json
from lxml import etree
from collections import OrderedDict
from log import testlog
from pprint import pprint
import traceback
# import html
from ip import *
from suds.client import Client
from concurrent.futures import ThreadPoolExecutor
import os
from html.parser import HTMLParser
import multiprocessing
import queue
from operator import itemgetter
from itertools import groupby
import concurrent
def WebConfig(client,dict_config):
    clientid = dict_config['clientID']
    resulttask =  client.service.getTask(clientid)
    
    testlog('webservice resulttask is %s,len(resulttask)=%s'%(resulttask,len(resulttask)))
    global count_total
    with lock:
        with lock_t:
        # count_total = manager.Value('tmp', len(resulttask))
            count_total.value += len(resulttask)
            testlog('count_total = {}'.format(count_total))
    taskid = []
    style = []
    configversion = []
    seedid = []
    configid = []
    taskparams = []
    needproxy = []
    s_config = []
    fp = []
    listtask = []
    level = []
    rate = []
    loginconfigVersion = []
    #[fileLink]⊥http://web2.chinagrain.gov.cn/n16/n1122/n2082/n4683307.files/n4683275.rar∧[link]⊥/n16/n1122/n2082/4683307.html
    try:
        for i in range(len(resulttask)):
            taskid.append(resulttask[i]['taskId'])
            style.append(resulttask[i]['type'])
            seedid.append(resulttask[i]['seedId'])
            needproxy.append(resulttask[i]['needProxy'])
            configversion.append(resulttask[i]['configVersion'])
            configid.append(resulttask[i]['configid'])
            level.append(resulttask[i]['level'])
            rate.append(resulttask[i]['rate'])
            loginconfigVersion.append((resulttask[i]['loginconfigVersion']))
            # if len(resulttask[i]) > 10:
            try:
                taskparams.append(resulttask[i]['taskParams'])
            except:
                taskparams.append('')
            # else:
            #     taskparams.append('')
    except IndexError:
        traceback.print_exc()
        raise IOError('task is None from webservice')
        # return ['0']
    dir1 = []
    for i in range(len(resulttask)):
        dirstr = (r'./%s.txt' % configid[i])
        dirstr = os.path.normcase(dirstr)
        dir1.append(dirstr)
        dictserver = {}
        dictserver['taskid'] = taskid[i]
        dictserver['client'] = client
        dictserver['configversion'] = configversion[i]
        dictserver['style'] = style[i]
        dictserver['taskparams'] = taskparams[i]
        dictserver['seedid'] = seedid[i]
        dictserver['configid'] = configid[i]
        dictserver['needproxy'] = needproxy[i]
        dictserver['clientid'] = clientid
        dictserver['level'] = level[i]
        dictserver['rate'] = rate[i]
        dictserver['loginconfigVersion'] = loginconfigVersion[i]
        listtask.append(dictserver)
    # for i in range(len(resulttask)):
        # listtask.append('')
        # listtask[i] = dictserver
        if os.path.exists(dir1[i]):
            fp.append(open(dir1[i]))
            try:
                s_config.append(json.load(fp[i],encoding='utf-8'))
           
                #s_config.append(ss_config)
                fp[i].close()
                
                # print(s_config[i]['version'],str(configversion[i]))
                if float(s_config[i]['version']) >= float(configversion[i]):
                    
                    dictserver['s_config'] = s_config[i]
                    
                    # listtask[i] = (s_config[i],taskid[i],client,configversion[i],configid[i],style[i],taskparams[i],seedid[i],needproxy[i])
                    testlog('taskconfigfile no update')
                    # return list
                else:
                #说明配置文件有更新
                    result =  client.service.getTaskConf(clientid,configid[i],'page')
                    #print ('------result.confContent = %s') %result.confContent
                    #print ('getTaskConf[0]=%s') %result[0]
                    #print client.last_received()
                    beforechangestring = '"version": "{}"'.format(float(s_config[i]['version']))
                    afterchangestring = '"version": "{}"'.format(float(configversion[i]))
                    result.confContent.replace(beforechangestring,afterchangestring)
                    s_config[i] = json.loads(result.confContent,encoding='utf-8')
                    
                    with open(dir1[i],'w') as f:
                        f.write(result.confContent)
                    
                    dictserver['s_config'] = s_config[i]
                   
                    # listtask[i] = (s_config[i],taskid[i],client,configversion[i],configid[i],style[i],taskparams[i],seedid[i],needproxy[i])
                    # testlog(listtask[i])
                    testlog('taskconfigfile is updated')
                    # return list
            except:
                traceback.print_exc()
                s_config.append('json analyse fail!')
                
                dictserver['s_config'] = s_config[i]
                
                # listtask[i] = (s_config[i],taskid[i],client,configversion[i],configid[i],style[i],taskparams[i],seedid[i],needproxy[i])

        else:
            #说明是第一次取到该任务写入配置文件
            result =  client.service.getTaskConf(clientid,configid[i],'page')
            #print ('------result.confContent = %s') %result.confContent
            #print ('getTaskConf[0]=%s') %result[0]
            #print client.last_received()
            try:

                s_config.append(json.loads(result.confContent,encoding='utf-8'))
                
                dictserver['s_config'] = s_config[i]
                
                # listtask[i] = (s_config[i],taskid[i],client,configversion[i],configid[i],style[i],taskparams[i],seedid[i],needproxy[i])
                with open(dir1[i],'w') as f:
                    f.write(result.confContent)
            except:
                traceback.print_exc()
                s_config.append('json analyse fail!')
                
                dictserver['s_config'] = s_config[i]
                
                # listtask[i] = (s_config[i],taskid[i],client,configversion[i],configid[i],style[i],taskparams[i],seedid[i],needproxy[i])
            
            
            # return s,taskid[i],client,configversion[i],configid[i],type[i]
    # testlog(1111) 
    return listtask
#datastr按照配置文件抓取的需要内容
#content抓取的网页源码
def getcookies(client,clientId,seedid):
    cookies = ''
    try:
        cookies = client.service.getProxy(clientId,seedid)
    except:
        traceback.print_exc()

    return cookies


def getproxy(client,clientId,taskid,seedid):
    # client.keepalive = True   
    try:
        proxy = client.service.getcookie(clientId,taskid,seedid)
        testlog('proxy ={}'.format(proxy))
        testlog('ip ={}'.format(proxy['ip']))
        if 'no proxy' != proxy['ip']:
            if len(proxy) == 2:
            # if proxy['userName'] is None:
            # if 'userName' not in proxy:
                http = 'http://{}:{}'.format(proxy['ip'],proxy['port'])
                proxies = {'http':http}
            else:
                http = 'http://{}:{}@{}:{}/'.format(proxy['userName'],proxy['passWord'],proxy['ip'],proxy['port'])
                proxies = {'http':http}
        # auth = '{},{}'.format(proxy['userName'],proxy['passWord'])
        else :
            proxies = 'no proxy'

    except:
        traceback.print_exc()
        proxies = 'get proxy timeout'
        # auth = ('','')
    testlog('proxies={}'.format(proxies))
    return proxies

def backwebservice(config,flag,datastr,content,pagename,httpRetrunCode):
    print('httpRetrunCode={}'.format(httpRetrunCode))
    clientid = config['clientid']
    client = config['client']
    taskid = config['taskid']
    style = config['style']
    taskparam = config['taskparams']
    configid = config['configid']
    testlog('clientid = {},flag = {}'.format(clientid,flag))
    # if '100' == flag:
    #     global count_success
    #     with lock:
    #         count_success.value += 1
    # testlog('count_success = {}'.format(count_success))
    if style in [1,2] :
        while 1:
            try:
                result =  client.service.infoReturn(clientid,taskid,flag,datastr,content,pagename,'','',style,httpRetrunCode)
                if True == str(result).isdigit():
                    break
            except:
                # result =  client.service.infoReturn(clientid,taskid,flag,datastr,content,pagename,'','',style)
                testlog('backwebservice no return ,go on backwebservice !!!!!!!!!!!!! ')
                
        testlog('backwebservice result = {}'.format(result))
        
        global count_executed,count_total,count_success
        # testlog('before count_success = {},count_executed = {},count_total = {}'.format(count_success,count_executed,count_total))
        if 100 == result:
            with lock:
                with lock_t:
                    count_success.value += 1
                    # testlog('count_success = {}'.format(count_success))
        with lock:
            with lock_t:
                count_executed.value += 1
                # testlog('count_executed = {}'.format(count_executed))
                count_total.value -= 1
                # testlog('count_total = {}'.format(count_total))  
        testlog('after count_success = {},count_executed = {},count_total = {}'.format(count_success,count_executed,count_total))

    elif 3 == style:
    #[fileLink]⊥http://web2.chinagrain.gov.cn/n16/n1122/n2082/n4683307.files/n4683275.rar∧[link]⊥/n16/n1122/n2082/4683307.html
        filelink = taskparam.split('∧')[0].split('⊥')[1]
        filename,filetype = download(filelink,configid)
        while 1:
            try:
                result =  client.service.infoReturn(clientid,taskid,flag,datastr,content,pagename,'','',style,httpRetrunCode)
                if True == str(result).isdigit():
                    break
            except:
                # result =  client.service.infoReturn(clientid,taskid,flag,datastr,content,pagename,'','',style)
                testlog('backwebservice no return ,go on backwebservice !!!!!!!!!!!!! ')
                
        testlog('backwebservice result = {}'.format(result))
        
        # global count_executed,count_total,count_success,count_tmp
        # testlog('before count_success = {},count_executed = {},count_total = {}'.format(count_success,count_executed,count_total))
        if 100 == result:
            with lock:
                with lock_t:
                    count_success.value += 1
                    # testlog('count_success = {}'.format(count_success))
        with lock:
            with lock_t:
                count_executed.value += 1
                # testlog('count_executed = {}'.format(count_executed))
                count_total.value -= 1
                # testlog('count_total = {}'.format(count_total))  
        testlog('after count_success = {},count_executed = {},count_total = {}'.format(count_success,count_executed,count_total))
# s = requests.Session()
# s.headers.update(headers)
    return 0
    
    # return result
def s2d(s):
    d = {}
    for i in s.split('&'):
        k,v = i.split('=',1)
        d[k] = v
    return d

def s2cookies(s):
    if '' == s:
        return s
    d = {}
    for i in s.split(';'):
        k,v = i.split('=',1)
        d[k] = v
    return d

def Crawl(config,dicttask):
    # print dict['Url'],dict['Allowautoredirect'],dict['Timeout'],dict['headers']
    # testlog("dicttask['taskparam'] = {}".format(dicttask['taskparam']))
    client = config['client']
    clientid = config['clientid']
    taskid = config['taskid']
    seedid = config['seedid']
    needproxy = config['needproxy']
    URL = dicttask['Url']
    payload = dicttask['payload']
    needcookies = dicttask['needCookie']
    if dicttask['Method'].lower() == 'get':
        if '' !=  dicttask['taskparam'] and None != dicttask['taskparam']:

            URL = dicttask['Url'].replace(dicttask['taskparam'].split('∧')[0].split('⊥')[0],dicttask['taskparam'].split('∧')[0].split('⊥')[1])
            if '[' in URL:
                URL = dicttask['Url'].replace(dicttask['taskparam'].split('∧')[1].split('⊥')[0],dicttask['taskparam'].split('∧')[1].split('⊥')[1])

    elif dicttask['Method'].lower() == 'post':
        # if 'taskparam' in dicttask:
        if '' !=  dicttask['taskparam'] and None != dicttask['taskparam']:
            payload = payload.replace(dicttask['taskparam'].split('∧')[0].split('⊥')[0],dicttask['taskparam'].split('∧')[0].split('⊥')[1])
            if '[' in payload:
                payload = payload.replace(dicttask['taskparam'].split('∧')[1].split('⊥')[0],dicttask['taskparam'].split('∧')[1].split('⊥')[1])
    
     

    # testlog(threading.current_thread())
    testlog("URL = {} ,{}".format(URL,threading.current_thread()))
    proxies = {}
    testlog('needproxy={}'.format(needproxy))
    if needproxy :
        testlog('开始申请代理。。。')
        proxies = getproxy(client,clientid,taskid,seedid)
        testlog('获得的proxies={}'.format(proxies))
    if 'no proxy' == proxies :
        testlog('No available proxy, task is abandon!')
        global count_executed,count_total
        count_executed.value += 1
        count_total.value -=1
        return -1
    if 'get proxy timeout' == proxies:
        flag = 90
        return backwebservice(config,flag,'','','')
    # testlog(dicttask)
    _cookies = ''
    if 'true' == needcookies.lower():
        res = getcookies(client,clientid,seedid)
        dt = res.absoluteTimeout.replace(tzinfo=None)
        # testlog(111111,datetime.datetime.now(),dt)
        date = dt - datetime.datetime.now().replace(tzinfo=None)
        # testlog(111111,datetime.datetime.now().replace(tzinfo=None),dt)
        if date > datetime.timedelta(seconds=1):
            _cookies = res.cookieContent
    Allowautoredirect = False
    if  'false' == dicttask['Allowautoredirect']:
        Allowautoredirect = False
    elif 'true' == dicttask['Allowautoredirect']:
        Allowautoredirect = True
    # testlog(s2d(dicttask['payload']))
    # testlog(1,Allowautoredirect)
    testlog('payload={}'.format(payload))
    # testlog(dicttask['Timeout'],payload,dicttask['headers'],proxies)
    flag = 100
    try:
        # s = requests.Session()
        # time.sleep(random.uniform(0,2))
        testlog("开始爬取网页。。。float(dicttask['Timeout']) = {}".format(float(dicttask['Timeout'])))
        if dicttask['Method'].lower() == 'get':
        # time.sleep(1)
            r = requests.get(URL,allow_redirects=Allowautoredirect,timeout=float(dicttask['Timeout']),headers=dicttask['headers'],proxies=proxies,cookies=s2cookies(_cookies))
        #r = requests.get(dicttask['Url'],timeout=dicttask['Timeout'])
        # time.sleep(1)
        elif dicttask['Method'].lower() == 'post':
            r = requests.post(URL,timeout=float(dicttask['Timeout']),data=s2d(payload),headers=dicttask['headers'],proxies=proxies,cookies=s2cookies(_cookies))
    except requests.exceptions.ConnectTimeout:
        flag = 98 #取页面超时
        return backwebservice(config,flag,'','','')
    except:
        traceback.print_exc()
        flag = 96 #取页面失败
        return backwebservice(config,flag,'','','')
    # testlog('r.encoding=%s'%r.encoding)
    # charset = re.compile(r'content="text/html;.?charset=(.*?)"').findall(r.text)
    # if not charset:
    #     r.encoding = (charset)
    r.encoding = dicttask['Encoding'].lower()
    content = r.text
    if content.find('<!--') > -1:
        content = re.sub(r'<!--.*?>','',content)
    # p = HTMLParser()
    # content = p.unescape(content)
    # print('content = %s'%content)
    testlog("r.status_code = {}".format(r.status_code))
    httpRetrunCode = r.status_code
    if r.status_code in [404,406,407,503]:
        flag = 96 #取页面失败
    #看登录成功状态 r.ok
    # with open(dirhtml,'w') as f:
    #     f.write(content)
    return content,flag,httpRetrunCode

def formatstr(xpathstring,lastn=0):
    num = xpathstring.count('{0}')
    if 1 == num:
        # return xpathstring[:xpathstring.index('[{0}]')]+xpathstring[len('[{0}]')+xpathstring.index('[{0}]'):]
        return xpathstring[:xpathstring.index('[{0}]')]
    elif 2 == num:
        # testlog(11,lastn)
        xpathstring = xpathstring[:xpathstring.index('[{0}]')] + '['+ str(lastn) + ']' + xpathstring[len('[{0}]') + xpathstring.index('[{0}]'):]
        # testlog(111111,xpathstring)
        # testlog(1111111,xpathstring[:xpathstring.index('[{0}]')])
        return xpathstring[:xpathstring.index('[{0}]')]
        
    elif 0 == num:
        return xpathstring
    
def leng(forstart1,tree,lastn=0):
    # global tree
    # testlog(111122,lastn)
    nodes = tree.xpath(buquan(formatstr(forstart1,lastn)))
    # for node in nodes:
        # print (node.text.strip())
    return len(nodes)

def listxunhuan(jsondir,dicttask,m,n,i,tree,p,lastn=0):
    if '/@' not in dicttask['lists'][m][i]['region'] and 'true' == dicttask['lists'][m][i]['IsAttributeValue'].lower() and dicttask['lists'][m][i]['ExtractorObject'].lower() not in ['innerhtml','outerhtml']:
        region = dicttask['lists'][m][i]['region'] + '/@' + dicttask['lists'][m][i]['ExtractorObject']
    # elif 'false' == dicttask['lists'][m][i]['IsAttributeValue'] and 'innertext' == dicttask['lists'][m][i]['ExtractorObject']:
    #     region = region + r'//text()'
    else:
        region = dicttask['lists'][m][i]['region'] 
    if 'true' == dicttask['lists'][m][i]['IsAttributeValue'].lower() and '' != dicttask['lists'][m][i]['Filter']:
        testlog('buquan(xunhuan(region,n,lastn) = {}'.format(buquan(xunhuan(region,n,lastn))))
        testlog('tree.xpath(buquan(xunhuan(region,n,lastn))) = {}'.format(tree.xpath(buquan(xunhuan(region,n,lastn)))))
        try:
            html = p.unescape(tree.xpath(buquan(xunhuan(region,n,lastn)))[0])
        except:
            html = p.unescape(tree.xpath(buquan(xunhuan(region,n,lastn))))
        if '/@' in region:       
            try:                 
                # testlog('1111111111',tree.xpath(buquan(xunhuan(region,n)))[0]) 
                jsondir[dicttask['lists'][m][i]['standardName']] = re.search(dicttask['lists'][m][i]['Filter'],html).group()
            except:
                jsondir[dicttask['lists'][m][i]['standardName']] = ''
        else:
            try:
                # testlog('2222222222',tree.xpath(buquan(xunhuan(region,n)))[0].text)
                jsondir[dicttask['lists'][m][i]['standardName']] = re.search(dicttask['lists'][m][i]['Filter'],html.text).group()
            except:
                jsondir[dicttask['lists'][m][i]['standardName']] = ''
    elif 'true' == dicttask['lists'][m][i]['IsAttributeValue'].lower() and '' == dicttask['lists'][m][i]['Filter']:
        if '/@' in region:
            jsondir[dicttask['lists'][m][i]['standardName']] = tree.xpath(buquan(xunhuan(region,n,lastn)))[0]
            # testlog(tree.xpath(buquan(xunhuan(region,n))))
            # testlog(tree.xpath(buquan(xunhuan(region,n)))[0])
        else:
            jsondir[dicttask['lists'][m][i]['standardName']] = tree.xpath(buquan(xunhuan(region,n,lastn)))[0].text.strip('\\r\\n\\t \r\n\t')

    elif 'false' == dicttask['lists'][m][i]['IsAttributeValue'].lower() and '' == dicttask['lists'][m][i]['Filter']:
        # testlog(dicttask['lists'][m][i]['region'])
        if 'outerhtml' != dicttask['lists'][m][i]['ExtractorObject'].lower() :
            # region = region + r'//text()'
            if '/@' in region:
                # testlog("11111region={}".format(region))
                try:
                    jsondir[dicttask['lists'][m][i]['standardName']] = tree.xpath(buquan(xunhuan(region,n,lastn)))[0]
                except:
                    # traceback.print_exc()
                    jsondir[dicttask['lists'][m][i]['standardName']] = ''
            else:
                # testlog("22222region={}".format(region))
                try:
                    # testlog("22222tree.xpath(buquan(xunhuan(region,n)))[0].text={}".format(tree.xpath(buquan(xunhuan(region,n)))[0].text))
                    jsondir[dicttask['lists'][m][i]['standardName']] = tree.xpath(buquan(xunhuan(region,n,lastn)))[0].text.strip('\\r\\n\\t \r\n\t')
                    # testlog("tree.xpath(buquan(xunhuan(region,n)))[0].text={}".format(tree.xpath(buquan(xunhuan(region,n)))[0].text))
                except:
                    # traceback.print_exc()
                    jsondir[dicttask['lists'][m][i]['standardName']] = ''
                # jsondir[dicttask['lists'][m][i]['standardName']] = tree.xpath(buquan(xunhuan(region,n)))[0].text
        elif 'outerhtml' == dicttask['lists'][m][i]['ExtractorObject'].lower():
            if '/@' in region:
                jsondir[dicttask['lists'][m][i]['standardName']] = tihuan(etree.tostring(tree.xpath(buquan(xunhuan(region,n,lastn)))[0]).decode())
            else:
                # testlog('etree.tostring(tree.xpath(buquan(xunhuan(region,n)))[0]={}'.format(etree.tostring(tree.xpath(buquan(xunhuan(region,n)))[0])))
                # testlog('etree.tostring(tree.xpath(buquan(xunhuan(region,n)))[0].text={}'.format(etree.tostring(tree.xpath(buquan(xunhuan(region,n)))[0].text)))
                # testlog('html.escape(etree.tostring(tree.xpath(buquan(xunhuan(region,n)))[0]))={}'.format(html.escape(etree.tostring(tree.xpath(buquan(xunhuan(region,n)))[0]).decode())))
                # jsondir[dicttask['lists'][m][i]['standardName']] = html.escape(etree.tostring(tree.xpath(buquan(xunhuan(region,n)))[0]).decode())
                jsondir[dicttask['lists'][m][i]['standardName']] = tihuan(etree.tostring(tree.xpath(buquan(xunhuan(region,n,lastn)))[0]).decode())
    elif 'false' == dicttask['lists'][m][i]['IsAttributeValue'] and '' != dicttask['lists'][m][i]['Filter']:
        if 'outerhtml' != dicttask['lists'][m][i]['ExtractorObject'].lower():
            try:
                html = p.unescape(tree.xpath(buquan(xunhuan(region,n,lastn)))[0])
            except:
                html = p.unescape(tree.xpath(buquan(xunhuan(region,n,lastn))))
            if '/@' in region:
                try:
                    jsondir[dicttask['lists'][m][i]['standardName']] = re.search(dicttask['lists'][m][i]['Filter'],html).group()
                except:
                    jsondir[dicttask['lists'][m][i]['standardName']] = ''
            else:
                try:
                    jsondir[dicttask['lists'][m][i]['standardName']] = re.search(dicttask['lists'][m][i]['Filter'],html).group()
                except:
                    jsondir[dicttask['lists'][m][i]['standardName']] = ''
        elif 'outerhtml' == dicttask['lists'][m][i]['ExtractorObject'].lower():
            html = p.unescape(tihuan(etree.tostring(tree.xpath(buquan(xunhuan(region,n,lastn)))[0]).decode()))
            # testlog(11,html)
            if '/@' in region:
                try:
                    jsondir[dicttask['lists'][m][i]['standardName']] = re.search(dicttask['lists'][m][i]['Filter'],tihuan(html)).group()
                except:
                    jsondir[dicttask['lists'][m][i]['standardName']] = ''
            else:
                try:
                    # testlog(html)
                    # html = p.unescape(tihuan(etree.tostring(tree.xpath(buquan(xunhuan(region,n)))[0]).decode()))
                    # testlog(1,dicttask['lists'][m][i]['Filter'])
                    # testlog(2,re.search( dicttask['lists'][m][i]['Filter'],tihuan(html)).group())
                    jsondir[dicttask['lists'][m][i]['standardName']] = re.search( dicttask['lists'][m][i]['Filter'],tihuan(html)).group()
                except:
                    jsondir[dicttask['lists'][m][i]['standardName']] = ''
                # testlog(111,jsondir[dicttask['lists'][m][i]['standardName']])
    # testlog(22,jsondir)
def xunhuan(xpathstring,n,lastn=0):
    num = xpathstring.count('{0}')
    # try:
    if 1 == num:
        return xpathstring[:xpathstring.index('[{0}]')] + '[' + str(n) + ']' + xpathstring[xpathstring.index('[{0}]') + len('[{0}]'):]
    elif 2 == num:
        xpathstring = xpathstring[:xpathstring.index('[{0}]')] + '[' + str(lastn) + ']' + xpathstring[xpathstring.index('[{0}]') + len('[{0}]'):]
        return xpathstring[:xpathstring.index('[{0}]')] + '[' + str(n) + ']' + xpathstring[xpathstring.index('[{0}]') + len('[{0}]'):]
    elif 0 == num:
        return xpathstring

def pagetree(dicttask,content,data_summary,tree,p,pagename):
    try:
        if dicttask['pages']:

            for i in range(len(dicttask['pages'][0])):
                # testlog("123123123len(dicttask['pages']) = {}".format(len(dicttask['pages'][0])))
                # testlog("123123123i = {}".format(i))
                # print("i = {}".format(i))
                # property = dicttask['pages'][0][i]['ExtractorObject']
                #region = ''
                if '/@' not in dicttask['pages'][0][i]['region'] and 'true' == dicttask['pages'][0][i]['IsAttributeValue'].lower() and dicttask['pages'][0][i]['ExtractorObject'].lower() not in ['innerhtml','outerhtml']:
                    region = dicttask['pages'][0][i]['region'] + '/@' + dicttask['pages'][0][i]['ExtractorObject']
                else:
                    region = dicttask['pages'][0][i]['region']
                testlog("dicttask['pages'] = {}".format(dicttask['pages']))
                if 'innertext' == dicttask['pages'][0][i]['ExtractorObject'].lower():
                    if '' != region:
                        nodes = tree.xpath(buquan(region))
                        # testlog("buquan(region) = {}".format(buquan(region)))
                        # print('region={}'.format(region))
                        # testlog('nodes ={}'.format(nodes))
                        for node in nodes:
                            # print(node.text)
                            if '/@' not in buquan(region):
                                # testlog(dicttask['pages'][0][i]['Filter'],dicttask['pages'][0][i]['standardName'],pagename,data_summary)
                                panduan(dicttask['pages'][0][i]['Filter'],dicttask['pages'][0][i]['standardName'],pagename,buquan(region),node.text,data_summary)
                            else:
                                panduan(dicttask['pages'][0][i]['Filter'],dicttask['pages'][0][i]['standardName'],pagename,buquan(region),node,data_summary)
                    else:
                        panduan(dicttask['pages'][0][i]['Filter'],dicttask['pages'][0][i]['standardName'],pagename,buquan(region),content,data_summary)
                else:
                    if '' != region:
                        nodes = tree.xpath(buquan(region))
                        # testlog("buquan(region) = {}".format(buquan(region)))
                        # print('region={}'.format(region))
                        # testlog('nodes ={}'.format(nodes))

                        # for node in nodes:
                            # print(node)
                        tt = etree.tostring(nodes[0]).decode()#属性里面的单引号变成双引号了
                        # print('tt = {}'.format(tt))
                        # tt = '"' + tt + '"'
                        # testlog('1tt = {}'.format(tt))
                        # testlog('p.unescape(tt) = {}'.format(tihuan(p.unescape(tt))))
                        tt = p.unescape(tt)  #此处没有替换为中文“，因为有的配置是用"current"正则匹配的页码
                            # testlog(dicttask['pages'][0][i]['Filter'],dicttask['pages'][0][i]['standardName'],pagename,data_summary)
                        panduan(dicttask['pages'][0][i]['Filter'],dicttask['pages'][0][i]['standardName'],pagename,buquan(region),tt,data_summary)
                    else:
                        panduan(dicttask['pages'][0][i]['Filter'],dicttask['pages'][0][i]['standardName'],pagename,buquan(region),content,data_summary)
    except:
        traceback.print_exc()
    
def Tree(content,listname,pagename,dicttask,data,data_summary,hanglie):
    
    # soup = BeautifulSoup(content,'lxml')
    # with open(r'.\sourceHtml_beautifulsoup.html','w') as fb:
        # fb.write(soup.prettify())
    #tree = etree.HTML(soup.prettify())
    # testlog("dicttask = {}".format(dicttask))
    # pprint("dicttask = {}".format(dicttask))
    tree = etree.HTML(content[0])
    p = HTMLParser()
    # print("content = {}".format(content))
    testlog('dicttask = {},data = {}'.format(dicttask,data))
    # print(222222222222222222222222)
    # print("dicttask['pages'] = {}".format(dicttask['pages']))
    # print("len(dicttask['pages'][0])={}".format(len(dicttask['pages'][0])))
    pagetree(dicttask,content,data_summary,tree,p,pagename)

    jsondir = OrderedDict()
    jsondir_tmp = OrderedDict()
    #jsondir = {}
    # testlog(121)
    _list_tm = []
    if hanglie == 'row':
        try:
            isqiantao = 0 #配置没有嵌套
            testlog("len(dicttask['lists']) = {}".format(len(dicttask['lists'])))
            for m in range(len(dicttask['lists'])):
                if 1 == m:
                    break
                if 1 < len(dicttask['lists']):
                    isqiantao = 1 #配置有嵌套
                    testlog('isqiantao is {}'.format(isqiantao))
                    # jsondir_tmp[dicttask['lists'][m+1][0]['ColumnStandardName']] = _list_tm
            # testlog("len(dicttask['lists']) = {}".format(len(dicttask['lists'])))
            # testlog("len(dicttask['lists'][m] = {}".format(len(dicttask['lists'][m])))
                
                StartChildPostion = int(dicttask['lists'][m][0]['StartChildPostion'])
                IntervalPosition = int(dicttask['lists'][m][0]['IntervalPosition'])
                LastChildPostion = IntervalPosition*(leng(dicttask['lists'][m][0]['region'],tree)+1-int(dicttask['lists'][m][0]['LastChildPostion']))
                testlog("StartChildPostion = {}".format(StartChildPostion))
                testlog("IntervalPosition = {}".format(IntervalPosition))
                testlog("LastChildPostion = {}".format(LastChildPostion))
                if '{0}' not in dicttask['lists'][m][0]['region']:  #详情页
                    StartChildPostion, LastChildPostion, IntervalPosition = 1,2,1
                for n in range(StartChildPostion, LastChildPostion, IntervalPosition):   #列表页
                    for i in range(len(dicttask['lists'][m])):
                        listxunhuan(jsondir,dicttask,m,n,i,tree,p)
                    if 1 == isqiantao:
                        StartChildPostion_qiantao = int(dicttask['lists'][m+1][0]['StartChildPostion'])
                        IntervalPosition_qiantao = int(dicttask['lists'][m+1][0]['IntervalPosition'])
                        testlog("dicttask['lists'][m+1][0]['region'] = {}".format(dicttask['lists'][m+1][0]['region']))
                        LastChildPostion_qiantao = IntervalPosition*(leng(dicttask['lists'][m+1][0]['region'],tree,n)+1-int(dicttask['lists'][m+1][0]['LastChildPostion']))
                        testlog("StartChildPostion_qiantao = {}".format(StartChildPostion_qiantao))
                        testlog("IntervalPosition_qiantao = {}".format(IntervalPosition_qiantao))
                        testlog("LastChildPostion_qiantao = {}".format(LastChildPostion_qiantao))
                        # time.sleep(5)

                        for n_qiantao in range(StartChildPostion_qiantao, LastChildPostion_qiantao, IntervalPosition_qiantao):
                            for i_qiantao in range(len(dicttask['lists'][m+1])):
                                listxunhuan(jsondir_tmp,dicttask,m+1,n_qiantao,i_qiantao,tree,p,n)
                                # testlog('jsondir_tmp = {}'.format(jsondir_tmp))
                                jsondir[dicttask['lists'][m+1][0]['ColumnStandardName']] = _list_tm
                            _list_tm.append(jsondir_tmp)
                            jsondir_tmp = OrderedDict()
                            # testlog('_list_tm = {}'.format(_list_tm))
                        _list_tm = []

                    listname.append(jsondir)
                    jsondir = OrderedDict()
        except:
            traceback.print_exc()
    elif hanglie == 'column':

        try:
            _list_t = []
            for m in range(len(dicttask['lists'])):
                for i in range(len(dicttask['lists'][m])):
            # testlog("len(dicttask['lists']) = {}".format(len(dicttask['lists'])))
            # testlog("len(dicttask['lists'][m] = {}".format(len(dicttask['lists'][m])))
                    StartChildPostion = int(dicttask['lists'][m][i]['StartChildPostion'])
                    IntervalPosition = int(dicttask['lists'][m][i]['IntervalPosition'])
                    LastChildPostion = IntervalPosition*(leng(dicttask['lists'][m][i]['region'],tree)+1-int(dicttask['lists'][m][i]['LastChildPostion']))
                    testlog("StartChildPostion = {}".format(StartChildPostion))
                    testlog("IntervalPosition = {}".format(IntervalPosition))
                    testlog("LastChildPostion = {}".format(LastChildPostion))
                    _list = []
                    if '{0}' not in dicttask['lists'][m][i]['region']:  #详情页
                        StartChildPostion, LastChildPostion, IntervalPosition = 1,2,1
                    for n in range(StartChildPostion, LastChildPostion, IntervalPosition):   #列表页
                        # _list_1 = []
                        _list_tmp = []
                        _region = dicttask['lists'][m][i]['region']
                        testlog('_region = {}'.format(_region))
                        _filter = dicttask['lists'][m][i]['Filter']
                        _ExtractorObject = dicttask['lists'][m][i]['ExtractorObject'].lower()
                        _IsAttributeValue = dicttask['lists'][m][i]['IsAttributeValue'].lower()
                        _standardName = dicttask['lists'][m][i]['standardName']
                        if '/@' not in dicttask['lists'][m][i]['region'] and 'true' == dicttask['lists'][m][i]['IsAttributeValue'] and dicttask['lists'][m][i]['ExtractorObject'].lower() not in ['innerhtml','outerhtml']:
                            _region = dicttask['lists'][m][i]['region'] + '/@' + dicttask['lists'][m][i]['ExtractorObject']
                        if 'innertext' == _ExtractorObject and 'false' == _IsAttributeValue:
                            nodes = tree.xpath(buquan(xunhuan(_region,n)))
                            testlog('nodes = {}'.format(nodes))
                            
                            if 0 == len(nodes):
                                _list_tmp.append([_standardName + ':' ])
                            for node in nodes:   
                                if '/@' in _region:
                                    if '' == _filter:
                                        # if 1 == len(nodes) :
                                        if 'column_ColumnStandardName' not in dicttask['lists'][m][i]:
                                            _list_tmp.append(_standardName + ':' + node)
                                            testlog('node = {}'.format(node))
                                        else:
                                            _list_tmp.append(_standardName + ':' + node +':' + dicttask['lists'][m][i]['column_ColumnStandardName'])
                                            testlog('node = {}'.format(node))
                                    else:
                                        # if 1== len(nodes):
                                        if 'column_ColumnStandardName' not in dicttask['lists'][m][i]:
                                            _text = re.search(_filter,node).group()
                                            testlog('_filter = {}'.format(_filter))
                                            _list_tmp.append(_standardName + ':' + _text)
                                            testlog('_text = {}'.format(_text))
                                        else:
                                            _text = re.search(_filter,node).group()
                                            testlog('_filter = {}'.format(_filter))
                                            _list_tmp.append(_standardName + ':' + _text + ':' + dicttask['lists'][m][i]['column_ColumnStandardName'] )
                                            testlog('_text = {}'.format(_text))
                                else:
                                    if '' == _filter:
                                        # if 1== len(nodes):
                                        if 'column_ColumnStandardName' not in dicttask['lists'][m][i]:
                                            _list_tmp.append(_standardName + ':' + node.text.strip('\\r\\n\\t \r\n\t') )
                                            testlog('node.text = {}'.format(node.text.strip('\\r\\n\\t \r\n\t')))
                                        else:
                                            _list_tmp.append(_standardName + ':' + node.text.strip('\\r\\n\\t \r\n\t') + ':' + dicttask['lists'][m][i]['column_ColumnStandardName'])
                                            testlog('node.text = {}'.format(node.text.strip('\\r\\n\\t \r\n\t')))
                                    else:
                                        # if 1== len(nodes):
                                        if 'column_ColumnStandardName' not in dicttask['lists'][m][i]:
                                            _text = re.search(_filter,node.text.strip('\\r\\n\\t \r\n\t')).group()
                                            _list_tmp.append(_standardName + ':' + _text)
                                            testlog('_text = {}'.format(_text))
                                        else:
                                            _text = re.search(_filter,node.text.strip('\\r\\n\\t \r\n\t')).group()
                                            _list_tmp.append(_standardName + ':' + _text + ':' + dicttask['lists'][m][i]['column_ColumnStandardName'])
                                            testlog('_text = {}'.format(_text))
                            # _list_1.append(_list_tmp)
                            
                        elif 'true' == _IsAttributeValue and  _ExtractorObject in  ['innerhtml','outerhtml']:
                            nodes = tree.xpath(buquan(xunhuan(_region,n)))
                            # _list_tmp = []
                            if 0 == len(nodes):
                                _list_tmp.append([_standardName + ':' ])
                            for node in nodes:
                                _html = p.unescape(tihuan(etree.tostring(node).decode()))
                                if '' == _filter:
                                    # if 1== len(nodes):
                                    if 'column_ColumnStandardName' not in dicttask['lists'][m][i]:
                                        _list_tmp.append(_standardName + ':' + _html)
                                    else:
                                        _list_tmp.append(_standardName + ':' + _html + ':' + dicttask['lists'][m][i]['column_ColumnStandardName'])
                                else:
                                    # if 1 == len(nodes):
                                    if 'column_ColumnStandardName' not in dicttask['lists'][m][i]:
                                        _html = re.search(_filter,_html)
                                        _list_tmp.append(_standardName + ':' + _html)
                                    else:
                                        _html = re.search(_filter,_html)
                                        _list_tmp.append(_standardName + ':' + _html + ':' + dicttask['lists'][m][i]['column_ColumnStandardName'])
                        #   _list_1.append(_list_tmp)
                            
                        elif 'true' == _IsAttributeValue and _ExtractorObject not in  ['innerhtml','outerhtml']:
                            nodes = tree.xpath(buquan(xunhuan(_region,n)))
                            # _list_tmp = []
                            if 0 == len(nodes):
                                _list_tmp.append([_standardName + ':'])
                            for node in nodes:   
                                if '/@' in _region:
                                    if '' == _filter:
                                        # if 1 == len(nodes):
                                        if 'column_ColumnStandardName' not in dicttask['lists'][m][i]:
                                            _list_tmp.append(_standardName + ':' + node)
                                            testlog('node = {}'.format(node))
                                        else:
                                            _list_tmp.append(_standardName + ':' + node + ':' + dicttask['lists'][m][i]['column_ColumnStandardName'])
                                            testlog('node = {}'.format(node))
                                    else:
                                        # if 1 == len(nodes):
                                        if 'column_ColumnStandardName' not in dicttask['lists'][m][i]:
                                            _text = re.search(_filter,node)
                                            _list_tmp.append(_standardName + ':' + _text)
                                            testlog('_text = {}'.format(_text))
                                        else:
                                            _text = re.search(_filter,node)
                                            _list_tmp.append(_standardName + ':' + _text + ':' + dicttask['lists'][m][i]['column_ColumnStandardName'])
                                            testlog('_text = {}'.format(_text))
                                else:
                                    if '' == _filter:
                                        # if 1 == len(nodes):
                                        if 'column_ColumnStandardName' not in dicttask['lists'][m][i]:
                                            _list_tmp.append(_standardName + ':' + node.text.strip('\\r\\n\\t \r\n'))
                                            testlog('node.text = {}'.format(node.text.strip('\\r\\n\\t \r\n')))
                                        else:
                                            _list_tmp.append(_standardName + ':' + node.text.strip('\\r\\n\\t \r\n') + ':' + dicttask['lists'][m][i]['column_ColumnStandardName'])
                                            testlog('node.text = {}'.format(node.text.strip('\\r\\n\\t \r\n')))
                                    else:
                                        # if 1 == len(nodes):
                                        if 'column_ColumnStandardName' not in dicttask['lists'][m][i]:
                                            _text = re.search(_filter,node.text).group()
                                            _list_tmp.append(_standardName + ':' + _text)
                                            testlog('_text = {}'.format(_text))
                                        else:
                                            _text = re.search(_filter,node.text).group()
                                            _list_tmp.append(_standardName + ':' + _text + ':' + dicttask['lists'][m][i]['column_ColumnStandardName'])
                                            testlog('_text = {}'.format(_text))
                        # _list_1.append(_list_tmp)
                        # testlog('_list_1 ={}'.format(_list_1))
                        _list.append(_list_tmp)
                    testlog('_list ={}'.format(_list))
                    _list_t.append(_list)
            # testlog('_list_t = {}'.format(_list_t))
            res_list = list(zip(*_list_t))
            testlog('121212,res_list = {}'.format(res_list))

            for ii in res_list:
                if ii:
                    _list_tt = []
                    _list_ttmp = []
                    stand = ''
                    name = ''
                    for i in ii:
                        
                        if 1 == i[0].count(':'): #不用循环的列
                            jsondir[i[0].split(':')[0]] = i[0].split(':')[1]
                        elif 2 == i[0].count(':'):#要循环的列
                            if '' != i[0].split(':')[1]:
                                _list_ttmp.append(i)
                                for iii in i:
                                    stand = iii.split(':')[2]
                                    name = iii.split(':')[0]

                            else:
                                # traceback.print_exc()
                                pass
                # _list_tt = []
                listlist = list(zip(*_list_ttmp))
                # testlog(1111,listlist)
                
                if listlist:
                    _list_l = []
                    for lt in listlist:
                        dict_tmp = {}
                        for ll in lt:
                            
                            # testlog(11111,ll)
                            if '' != ll.split(':')[1]:
                                
                                dict_tmp[ll.split(':')[0]] = ll.split(':')[1]
                        _list_l.append(dict_tmp)
                    jsondir[stand] = _list_l
                listname.append(jsondir)
                jsondir = OrderedDict()
        except:
            traceback.print_exc()
    # testlog('data = {}'.format(data)) 
    pprint('data = {}'.format(data))
    flag = content[1]
    try:
        datastr = json.dumps(data,ensure_ascii=False)
    # global flag
    except:
        # testlog(traceback.print_exc())
        datastr = ''
        flag = 99#fail
    # testlog('flag = {}'.format(flag))
    # testlog('listname = {}'.format(listname))
    
    return datastr,flag,listname
    
def Writetxt(dirtxt,datastr):
    with open(dirtxt,'w') as f:
        f.write(datastr)
def tihuan(s):
    s = s.replace('"','“')
    # s = s.replace("'",'‘')
    return s
def play(config,dict_config):
    try:
        # dict1 = {} #配置文件字段除了要循环的配置字段
        dict_data = OrderedDict()#存放配置文件的字典
        data = OrderedDict()#展示爬取json内容
        data_crawl = OrderedDict()
        data_summary = OrderedDict()
        listname = []#展示爬取list内容
        pagename = []
        # nodelist =[]#要循环行的配置字段
        list_tmp_list_global = []
        list_tmp_page_global = []
        # s, taskid, client, configversion, configid, style,taskparam,seedid = config[0], config[1], config[2], config[3], config[4], config[5],config[6],config[7]
        s = config['s_config']
        taskid = config['taskid']
        client = config['client']
        configversion = config['configversion']
        configid = config['configid']
        style = config['style']
        taskparam = config['taskparams']
        seeid = config['seedid']
        clientid = config['clientid']
        dirtxt = (r'./%sresult.txt' % configid)
        dirtxt = os.path.normcase(dirtxt)
        # dirhtml = (r'./%ssourceHtml.html' % configid)
        # print ('------s = %s') % s
        if s in ['0'] :
            raise IOError('task is None from webservice')
        # clientid = dict_config['clientID']
        if 'json analyse fail!' == s:
            flag = 1
            testlog('------flag = {}'.format(flag))
            return backwebservice(config,flag,'','','')
        
        hanglie = 'row'
        if 'mode' in s.keys():
            hanglie = s['mode']
        # testlog(1111111111111111111111)
        digui(s['ExtractConfig']['PathNode'],list_tmp_list_global,list_tmp_page_global,hanglie)
        # testlog(2222)
        dict_data['lists'] = list_tmp_list_global
        dict_data['pages'] = list_tmp_page_global
        # testlog("222222dict_data['pages']={}".format(dict_data['pages']))
        # testlog("222222dict_data['lists']={}".format(dict_data['lists']))
        dict_data['content'] = data_crawl
        if '' != s['ExtractConfig']['PathNode'][0]['ColumnStandardName']:
            data_crawl[s['ExtractConfig']['PathNode'][0]['ColumnStandardName']] = data_summary
        else:
            data_crawl['datasummary'] = data_summary
        # testlog("len(dict_data['lists'])={}".format(len(dict_data['lists'])))
        # testlog("dict_data['lists']={}".format(dict_data['lists']) )
        # testlog("dict_data['lists'][0][0]['ColumnStandardName']={}".format(dict_data['lists'][0][0]['ColumnStandardName']) )
        for i in range(len(dict_data['lists'])):
            data_summary[dict_data['lists'][0][i]['ColumnStandardName']] = listname
        # print("1111111111len(dict_data['pages'])={}".format(len(dict_data['pages'])))
        # print("dict_data['pages']={}".format(dict_data['pages']))

        dict_data['Timeout'] = (int)(s['pageRequest']['Timeout'])/1000
        dict_data['Encoding'] = s['pageRequest']['Encoding']
        dict_data['Url'] = s['pageRequest']['Url']
        dict_data['Method'] = s['pageRequest']['method']
        dict_data['payload'] = s['pageRequest']['DataTemplate']
        dict_data['Allowautoredirect'] = s['pageRequest']['allowAutoRedirect']
        dict_data['needCode'] = s['pageRequest']['needCode']
        # dict_data['needProxy'] = s['pageRequest']['needProxy']
        dict_data['needCookie'] = s['pageRequest']['needCookie']
        dict_data['Contenttype'] = s['pageRequest']['contentType']
        dict_data['Useragent'] = s['pageRequest']['UserAgent']
        dict_data['Accept'] = s['pageRequest']['accept']
        dict_data['Referer'] = s['pageRequest']['Referer']
        # dict1['args_pages'] = config_args_pages(s)
        dict_data['headers'] = ''
        if '' != dict_data['Accept'] and '' != dict_data['Useragent']:
            dict_data['headers'] = { 'Accept':dict_data['Accept'],
                    'User-Agent': dict_data['Useragent']
                    }
        dict_data['taskparam'] = taskparam
        # testlog(111)
        content = Crawl(config,dict_data)
        httpRetrunCode = content[2]
        if 1 == style:    #HTML爬取
            #testlog('1taskparam = %s') % taskparam
            # testlog('--------dict_data={}'.format(dict_data))
            # content = Crawl(client,clientid,taskid,dict_data,seedid)
            
            # testlog('content={}'.format(content))
            if -1 == content:
                testlog('No proxy, task is abandon!')
                flag = 96
                return -1
            elif 0 == content:
                return 0
            treelist = Tree(content,listname,pagename,dict_data,data,data_summary,hanglie)
            #testlog('treelist ={}'.format(treelist))
            datastr, flag, listname = treelist[0],treelist[1],treelist[2]
            Writetxt(dirtxt,datastr)
            resultname = dict_data['Url'] + '.txt'
            # testlog(resultname)
            if '100' != content[1]:
                flag = content[1]
            return backwebservice(config,flag,datastr,content[0],resultname,httpRetrunCode)
        elif 2 ==style :  #json爬取
            # content = Crawl(config,dict_data)
            # testlog('content={}'.format(content))
            if -1 == content:
                testlog('No proxy, task is abandon!')
                return -1
            elif 0 == content:
                return 0
        elif 3 ==style :  #下载任务
            #print('2taskparam = %s') % taskparam
            filelink = taskparam.split('∧')[0].split('⊥')[1]
            dict_data['Url'] = filelink
            #print('Url = %s') %filelink
            filename,filetype = download(filelink,configid)
            content = Crawl(config,dict_data)
            if -1 == content:
                testlog('No proxy task is abandon!')
                return -1
            elif 0 == content:
                return 0
            resultname = dict_data['Url'] + '.txt'
            # testlog(resultname)
            if '100' != content[1]:
                flag = content[1]
            return backwebservice(config,flag,'',content[0],resultname,httpRetrunCode)
    except Exception as e:
        traceback.print_exc()
    

def findconfig(filename):
    import xml.etree.ElementTree as Etree
    dict_config = {}
    # xml_str = open(".\client.exe.config",'r').read()
    # xml_str = open(filename,'r').read()
    # notify_data_tree = Etree.fromstring(xml_str)
    # print(xml_str)
    # xml_str = """<root><ot><title>i am title</title></ot></root>"""
    notify_data_tree = Etree.parse(filename)

    nodes = notify_data_tree.findall("appSettings/add")
    # print(nodes)
    for node in nodes:
        # print('key={},value={}'.format(node.attrib['key'],node.attrib['value'])) #>> i am title
        if 'webServicerAdd' == node.attrib['key']:
            dict_config['webServicerAdd'] = node.attrib['value']
        elif 'clientID' == node.attrib['key']:
            dict_config['clientID'] = node.attrib['value']
        elif 'maxTaskPool' == node.attrib['key']:
            dict_config['maxTaskPool'] = node.attrib['value']
        elif 'maxThreadNumber' == node.attrib['key']:
            dict_config['maxThreadNumber'] = node.attrib['value']
        elif 'tetchTaskTim' == node.attrib['key']:
            dict_config['tetchTaskTim'] = node.attrib['value']
        elif 'clientVersion' == node.attrib['key']:
            dict_config['clientVersion'] = node.attrib['value']
    if '' == dict_config['clientID']:
        xiugaixml(filename)
        findconfig(filename)

    return dict_config


# class WorkManager(object):
#     def __init__(self, work_num=[],thread_num=200,dict_config={}):
#         self.work_queue = queue.Queue()
#         self.threads = []
#         self.dict_config = dict_config
#         self.__init_work_queue(work_num)
#         self.__init_thread_pool(thread_num)

#     """
#         初始化线程
#     """
#     def __init_thread_pool(self,thread_num):
#         for i in range(int(thread_num)):
#             self.threads.append(Work(self.work_queue))

#     """
#         初始化工作队列
#     """
#     def __init_work_queue(self, jobs_num):
#         for i in jobs_num:
#             self.add_job(do_job, i,dict_config)

#     """
#         添加一项工作入队
#     """
#     def add_job(self, func, *args):
#         self.work_queue.put((func, list(args)))#任务入队，Queue内部实现了同步机制
#     """
#         检查剩余队列任务
#     """
#     def check_queue(self):
#         return self.work_queue.qsize()

#     """
#         等待所有线程运行完毕
#     """   
#     def wait_allcomplete(self):
#         for item in self.threads:
#             if item.isAlive():
#                 item.join()

# class Work(threading.Thread):
#     def __init__(self, work_queue):
#         threading.Thread.__init__(self)
#         self.work_queue = work_queue
#         self.start()    #如果是self.run()此处就是单线程

#     def run(self):
#         #死循环，从而让创建的线程在一定条件下关闭退出
#         while True:
#             try:
#                 do, args = self.work_queue.get(block=False,timeout = 100)#任务异步出队，Queue内部实现了同步机制
#                 do(args)
#                 self.work_queue.task_done()#通知系统任务完成
#             except Exception as e:
#                 print(str(e))
#                 break

#具体要做的任务
def do_job(args):

    r = play(args[0],args[1])
    if -1 == r:
        return -1
def digui(ss,list_tmp_list_global,list_tmp_page_global,hanglie):   
    try:
        for i in range(len(ss)):
            if 'DataNode' in ss[i] :
                list_tmp_list =[]
                list_tmp_page =[]
                for k in range(len(ss[i]['DataNode'])):
                    dict_tmp=OrderedDict()
                    # if 'row' == hanglie.lower():
                    dict_tmp['StartChildPostion'] = ss[i]['StartChildPostion']
                    dict_tmp['IntervalPosition'] = ss[i]['IntervalPosition']
                    dict_tmp['LastChildPostion'] = ss[i]['LastChildPostion']
                    if 'column' == hanglie.lower():
                        # testlog(11)
                        # print(1212121212,ss[i]['DataNode'][k])
                        if 'ColumnStandardName' in ss[i]['DataNode'][k]:
                           dict_tmp['column_ColumnStandardName'] = ss[i]['DataNode'][k]['ColumnStandardName']
                        # if 'ColumnStandardName' in ss[i]['DataNode'][k].keys():
                        if 'StartChildPostion' in ss[i]['DataNode'][k]:
                            dict_tmp['column_StartChildPostion'] = ss[i]['DataNode'][k]['StartChildPostion']
                            dict_tmp['column_IntervalPosition'] = ss[i]['DataNode'][k]['IntervalPosition']
                            dict_tmp['column_LastChildPostion'] = ss[i]['DataNode'][k]['LastChildPostion']
                            
                
                    dict_tmp['region'] = ss[i]['DataNode'][k]['region']
                    dict_tmp['order'] = ss[i]['DataNode'][k]['order']
                    dict_tmp['standardName'] = ss[i]['DataNode'][k]['standardName']
                    dict_tmp['ColumnType'] = ss[i]['DataNode'][k]['ColumnType']
                    dict_tmp['Comment'] = ss[i]['DataNode'][k]['Comment']
                    dict_tmp['Filter'] = ss[i]['DataNode'][k]['Filter']
                    dict_tmp['IsAttributeValue'] = ss[i]['DataNode'][k]['IsAttributeValue']
                    dict_tmp['ExtractorObject'] = ss[i]['DataNode'][k]['ExtractorObject']
                    dict_tmp['ColumnStandardName'] = ss[i]['ColumnStandardName']
                    if dict_tmp['standardName'].lower() in ['totalpage','currentpage','totalrecord']:
                        list_tmp_page.append(dict_tmp)
                    else :
                        list_tmp_list.append(dict_tmp)
                # list_tmp1.append(list_tmp)
                if list_tmp_list:
                    list_tmp_list_global.append(list_tmp_list)
                    # dict_data['lists'] = list_tmp_list1
                if list_tmp_page:
                    list_tmp_page_global.append(list_tmp_page)
            if 'PathNode' in ss[i] :
                digui(ss[i]['PathNode'],list_tmp_list_global,list_tmp_page_global,hanglie)
    except:
        traceback.print_exc()
def xiugaixml(filedir):
    import uuid
    f = open(filedir,'r')
    xmldata = f.read()
    s = '<add key="clientID" value="' + uuid.uuid1() + '"/>'
    xmldata = re.sub('\<add key="clientID" value="(.*?)\"/>',s,xmldata)
    f.close()
    f = open(filedir,'w')
    f.write(xmldata)
    f.close()
    # print(xmldata)

def buquan(s):
    r = re.sub('^html/','/html/',s)
    if re.search('^//',r) is None and re.search('^/[^h]',r) is not None:#有的xpath是/table[1],etree在解析时会自动补全成/html/body/table[1],所以xpath路径也要补全
        r =re.sub('^/','/html/body/',s)
    return r
def panduan(filters,sss,pagename,region,text,data_summary):
    
    try:
        p = HTMLParser()
        # html = p.unescape(tree.xpath(buquan(xunhuan(region,n)))[0])
        # testlog('p.unescape(text) ={}'.format(p.unescape(text)))
        dic_tmp = {}

        if '/@' in region or '' == region:
            # testlog(1212)
            if '' != filters:
                # testlog(12,re.search(filters,p.unescape(text)),p.unescape(text))
                if re.search(filters,p.unescape(text)) is not None:
                    dic_tmp[sss] = (re.search(filters,p.unescape(text))).group()
                else :
                    dic_tmp[sss] = ''
            elif '' == filters:
                dic_tmp[sss] = p.unescape(text)

        if '/@' not in region and '' != region:
            # testlog(2121)
            if '' != filters:
                testlog(text)
                # testlog(p.unescape(text))
                testlog(filters)
                testlog(re.search(filters,text))
                if re.search(filters,text) is not None:
                    dic_tmp[sss] = (re.search(filters,text)).group()
                else :
                    dic_tmp[sss] = ''
            elif '' == filters:
                dic_tmp[sss] = text
        # testlog(111)
        pagename.append(dic_tmp)
        data_summary[sss] = dic_tmp[sss]
    except:
        traceback.print_exc()
    # testlog('11111data_summary = {}'.format(data_summary))
def heartbeat(client,dict_config ,timenow):
    # ip = get_ip_address('eth0')
    # meminfo = memory_info()
    # sysinfo = sys_info()
    # diskstat = disk_stat()
    # cpuinfo = cpu_info()
    # cpu = cpu()
    # currentpath = os.path.realpath('crawl.py')
    # class ClientInfo(object):
    #     def __init__(self):
    #         self.Id = clientid
    #         self.ClientName = clientid
    #         self.Ip = get_ip_address('eth0')
    #         self.HostName = sys_info()[1]
    #         self.Version = '1.0'
    #         self.OsName = sys_info()[0]
    #         self.MemSize = memory_info()[0]
    #         self.MemUsed = memory_info()[1]
    #         self.CpuType = cpu_info()
    #         self.CpuState = cpu()
    #         self.ClientPath = os.path.realpath('crawl.py')
    #         self.DiskSize = disk_stat()['capacity']
    #         self.DiskRemainSize = float(disk_stat()['capacity'])-float(disk_stat()['used'])
    #         self.IeVersion = ''
    #         self.StartTime = timenow
    #         self.TaskTotal = ''
    #         self.TaskExecuted = ''
    # cli = ClientInfo()
    # print(cli.StartTime)
    # ParamResponse = client.service.heartBeating(cli)
    # return ParamResponse
    try:
        global count_executed,count_success,count_total
        cli = client.factory.create('clientInfo')
        cli.id = dict_config['clientID']
        cli.clientName = dict_config['clientID']
        cli.ip = get_ip_address('eth0')
        cli.hostName = sys_info()[1]
        cli.version = dict_config['clientVersion']
        cli.osName = sys_info()[0]
        cli.memSize = memory_info()[0]
        cli.memUsed = memory_info()[1]
        cli.cpuType = cpu_info()
        cli.cpuState = cpu()
        cli.clientPath = os.path.realpath('crawl.py')
        cli.diskSize = disk_stat()['capacity']
        cli.diskRemainSize = '{:.2f}'.format(float(disk_stat()['capacity'])-float(disk_stat()['used']))
        cli.ieVersion = 'no ie'
        cli.startTime = timenow
        
        cli.taskTotal = count_total.value
        cli.taskExecuted = count_executed.value

        #还有success字段暂时没传

        ParamResponse = client.service.heartBeating(cli)
        testlog('xintiao count_total = {},count_executed = {},count_success = {}'.format(count_total,count_executed,count_success))
        # testlog('ParamResponse = {}'.format(ParamResponse) )
        # testlog('ParamResponse[1] = {}'.format(ParamResponse[1]))
        # testlog("ParamResponse['fetchingInterval'] = {}".format(ParamResponse['fetchingInterval']))
        
        
        return ParamResponse
    except:
        return None
def dingshi(t):
    time.sleep(t)

def xintiao(t,client,dict_config,timenow):
    try:
        while True:
            
            # client = Client(dict_config['webServicerAdd'])
            ParamResponse = heartbeat(client,dict_config,timenow)
            if None != ParamResponse:
                ggg(ParamResponse)
                time.sleep(t)

    except:
        traceback.print_exc()
        
def work(Executor,dict_config,q_queue,d):

    try:
        # testlog('work currentpid is {}'.format(os.getpid()))
        f_list = []
        # with ThreadPoolExecutor(max_workers=threadSize) as Executor:
        for i in range(q_queue.qsize()):
            task = q_queue.get()
            if task['seedid'] in d:
                time.sleep(int(task['rate'])/1000)
                # testlog('{{}}休眠{0}，task = {1}'.format(int(task['rate'])/1000,task))
                future = Executor.submit(do_job,[task,dict_config])
                print(1212121212121)
                f_list.append(future)
            else:
                future = Executor.submit(do_job,[task,dict_config])
                f_list.append(future)
        concurrent.futures.wait(f_list)  #等待线程池任务结束
    except:
        traceback.print_exc()

def work_x(t,client,dict_config):
    try:

        while True:
            if p_queue.qsize() >= 2:
                for i in range(p_queue.qsize()-1):
                    p_queue.get()
            queue_gg = p_queue.get()
            gg = json.loads(queue_gg)
            # if int(gg['fetchingInterval']) > 0:
            #     time.sleep(gg['fetchingInterval'])
            threadSize = int(gg['threadSize'])
            print(1111,threadSize)
            if gg['isFetching'] :
                work_list = WebConfig( client,dict_config)   # work_list 未排序的任务池（列表）
                print(2222,work_list)
                work_list.sort(key = lambda x:(-int(x['level']),x['seedid'])) # work_list 排序后的任务池（列表）
                print(3333,work_list)
                q_queue = queue.Queue()    # q_queue 初始化任务队列
                d = {}   # 初始化种子池，用来保证种子和rate的一一对应
                print(4444)
                for _ , items in groupby(work_list,key=itemgetter('level','seedid')):
                    for i in items:
                        q_queue.put(i)
                        # print('',i)
                        seedid = i['seedid']
                        d[seedid] = i['rate']
                            # do_job(q_queue,d)
                            # with ThreadPoolExecutor(max_workers=threadSize) as Executor:
                            # Executor = ThreadPoolExecutor(max_workers=threadSize)
                print(5555)
                with ThreadPoolExecutor(max_workers=threadSize) as Executor:
                    work(Executor,dict_config,q_queue,d)
                    print(6666,dict_config,q_queue,d)
            # time.sleep(random.uniform(0,t))
    except:
        traceback.print_exc()
def ggg(ParamResponse):
    from collections import OrderedDict
    gg = OrderedDict()
    
    gg['fetchingSize'] = ParamResponse['fetchingSize']
    gg['isFetching'] = ParamResponse['isFetching']
    # gg['serverTime'] =time.strftime( ISOTIMEFORMAT, time.localtime( time.time() ) )
    # print("ParamResponse['serverTime'].split('.')[0] = {}".format(str(ParamResponse['serverTime']).split('.')[0]))
    gg['serverTime'] = str(ParamResponse['serverTime']).split('.')[0]
    gg['taskThreshold'] = ParamResponse['taskThreshold']
    gg['threadSize'] = ParamResponse['threadSize'] 
    gg['fetchingInterval'] = ParamResponse['fetchingInterval']
    # # with lock:
    # dirxintiao = r'xintiao.json'
    # dirxintiao = os.path.normcase(dirxintiao)
    testlog('xintiao currentpid is {}'.format(os.getpid()))
    # with open(dirxintiao,'w') as f:
    #     f.write(json.dumps(gg,ensure_ascii=False))
    p_queue.put(json.dumps(gg,ensure_ascii=False))
if __name__ == '__main__':
    try:
        ISOTIMEFORMAT = '%Y-%m-%d %X'
        filename=r'./client.exe.config'
        timenow = time.strftime( ISOTIMEFORMAT, time.localtime( time.time() ) )
        dict_config = findconfig(filename)
        client = Client(dict_config['webServicerAdd'],timeout=60*60*48)

        p_queue = multiprocessing.Queue()
        lock = multiprocessing.Lock()
        lock_t = threading.Lock()
        manager = multiprocessing.Manager()
        count_total = manager.Value('tmp', 0)
        count_executed = manager.Value('tmp', 0)
        count_success = manager.Value('tmp', 0)
        ParamResponse = heartbeat(client,dict_config,timenow)

        
     
        # ParamResponse = heartbeat(client,dict_config,timenow)


        w_xintiao = multiprocessing.Process(target=xintiao, args=(30,client,dict_config,timenow))
        w_xintiao.daemon = True
        w_xintiao.start()

        # threadspool = ThreadPoolExecutor(ParamResponse['threadSize'])

        work_x(1,client,dict_config)
        w_xintiao.join()
    except:
        traceback.print_exc()