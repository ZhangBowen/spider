#coding=utf-8
import getopt,sys,urllib2,re,os,time,json,HTMLParser,urllib
from selenium import webdriver
reload(sys)
sys.setdefaultencoding('utf-8')
'''

data = driver.find_element_by_id('jd-price').text
print data
'''
help = '''usage:
python ./spider.py -u base_url 
    -u: base_url.
    -q: quickly mode.
'''
try:
    args,opts = getopt.getopt(sys.argv[1:],"u:hq")
except:
    print "invalid args."
    print help
    exit(1)


re_conf = {'京东':{},'苏宁':{}}

suning_conf = re_conf['苏宁']
jd_conf = re_conf['京东']
FAST = False

#######################  jd  ###############################
jd_conf['next_page_prefix'] = "http://list.jd.com/list.html"

jd_conf['src_name'] = '京东'

jd_conf['next_page'] = []
jd_conf['next_page'].append(re.compile(r"<a href=\\\"([^>]*)\\\" class=\\\"next\\\">下一页.*"))

jd_conf['item'] = []
jd_conf['item'].append(re.compile(r"class=\\\"p-img\\\"><a target=\\\"_blank\\\" href=\\\"([^> ]*)\\\""))

jd_conf['key_word'] = 'jd.com'

jd_conf['brand'] = []
jd_conf['brand'].append(re.compile("<li>品牌：<a.*>(.*)</a></li>"))

jd_conf['name']  = []
jd_conf['name'].append(re.compile("商品名称：(.*)</li>"))

jd_conf['NO']    = []
jd_conf['NO'].append(re.compile("<li>商品编号：(.*)</li>"))

jd_conf['size']  = []
jd_conf['size'].append(re.compile("尺寸：(.*)</li>"))
jd_conf['size'].append(re.compile("屏幕尺寸</td><td>([^<]*)</td>"))
jd_conf['size'].append(re.compile("title>.*([\d\.]+英寸).*</title>"))

jd_conf['detail'] = []
jd_conf['detail'].append(re.compile("title>.*(?:（|\()(.*)(?:）|\)).*</title>"))

jd_conf['price']  = []
jd_conf['price'].append(re.compile("id=\"jd-price\">￥?([^<]*)<"))
jd_conf['price_url'] = 'http://p.3.cn/prices/get?skuid=J_'
def get_jd_price(url):
    res = urllib2.urlopen(url)
    res = json.loads(res.read())[0]['p'].encode('utf-8')
    return res
jd_conf['price_api'] = get_jd_price

jd_conf['discount'] = []
jd_conf['discount'].append(re.compile("<em class=\"hl_red\">([^<]*)</em"))

jd_conf['feedback'] = []
jd_conf['feedback'].append(re.compile("已有(\d*)人评价"))

################################################################


######################### su ning ##############################
suning_conf['next_page_prefix'] = "http://list.suning.com/" 

suning_conf['src_name'] = '苏宁'

suning_conf['next_page'] = []
suning_conf['next_page'].append(re.compile("class=\"next\" title=\"下一页\" href=\"([^>]*)\"><b></b>下一页"))

suning_conf['item'] = []
suning_conf['item'].append(re.compile("href='([^>]*)' target='_blank' name="))

suning_conf['key_word'] = 'suning.com'

suning_conf['brand'] = []
suning_conf['brand'].append(re.compile("品牌：</span>\n</div>\n</td>\n\n<td width=\"72%\" class=\"td1\">([^<]*)<"))

suning_conf['name']  = []
suning_conf['name'].append(re.compile("<h1 class=\"wb\" title=\"([^ \"]*)"))

suning_conf['NO']    = []
suning_conf['NO'].append(re.compile("商品编码</span>\n(\d*)"))

suning_conf['size']  = []
suning_conf['size'].append(re.compile("屏幕尺寸：</span>\n</div>\n</td>\n\n<td width=\"72%\" class=\"td1\">([^<]*)<"))

suning_conf['detail'] = []
suning_conf['detail'].append(re.compile("<h1 class=\"wb\" title=\".* .*(?:电脑|笔记本)(?:（|\()([^>]*)(?:）|\))"))

suning_conf['price']  = []
suning_conf['price'].append(re.compile("id=\"netPrice\">¥?<em>([^<]*)<"))
suning_conf['price'].append(re.compile("id=\"promotionPrice\">¥?<em>([^<]*)<"))

suning_conf['discount'] = []
suning_conf['discount'].append(re.compile("class=\"promotion-content hide\".*<em>([^<]*)</em"))

suning_conf['feedback'] = []
suning_conf['feedback'].append(re.compile("<h2><span>评价\((\d*)\)"))
################################################################

conf = None
driver = webdriver.PhantomJS()

time = time.strftime('%Y-%m-%d %H:%M:%S')

html_parser = HTMLParser.HTMLParser()

g_source = None

def search_info(src,res,is_all = False):
    for re in res:
        tmp = re.findall(src)
        if len(tmp) > 0:
            if is_all:
                return tmp
            else:
                return tmp[0]
    return '' if is_all==False else []

def get_item_data(url):
    
    print url
    try:
        if FAST == True:
            data = urllib2.urlopen(url)
            if conf['src_name'] == '京东':
                data = data.read().decode('gbk').encode('utf-8')
            else:
                data = data.read()
        else:
            driver.get(url)
            data = driver.page_source.encode('utf-8')
    except Exception,e:
        print "net error on item ",url,e
        return None
    try:
        brand = search_info(data,conf['brand'])
        name  = search_info(data,conf['name'])
        NO    = search_info(data,conf['NO'])
        size  = search_info(data,conf['size'])
        detail = search_info(data,conf['detail'])
        price = search_info(data,conf['price'])
        if price == '' and 'price_api' in conf:
            price = conf['price_api'](conf['price_url']+NO)
        discount_set = search_info(data,conf['discount'],True)
        feedback = search_info(data,conf['feedback'])
        if feedback == '':
            feedback = '0'
        discount = ';'.join([str(index+1)+': '+disinfo for index,disinfo in enumerate(discount_set)])
    except Exception,e:
        print 'error',e
        return None

    return (time,conf['src_name'],brand,name,NO,price,size,detail,discount,feedback)

    
    
def spider(url,limit):
    next_page_url = url
    next_page_prefix = conf['next_page_prefix']; 
    res = []
    while next_page_url != None:
        print next_page_url,'...'
        try:
            data = urllib2.urlopen(next_page_url)
            data = data.read()
        except Exception,e:
            print "net error on",next_page_url,"page:",e
            continue 


        item_list = search_info(data,conf['item'],True)
        for item_url in item_list:
            item_data = get_item_data(item_url)
            if item_data != None:
                res.append(item_data)

        tmp = next_page_url
        next_page_url = None
        tmp_url = search_info(data,conf['next_page'])
        if tmp_url!='':
            next_page_url = next_page_prefix+html_parser.unescape(tmp_url).encode('utf-8')

        if next_page_url == None or tmp == next_page_url:
            print 'end'
            break
        
        print 'done'

        
    return res

limit = {}
base_url = None
for arg,opt in args:
    if arg == '-u':
        base_url = opt
    elif arg=='-h':
        print help
        exit(0)
    elif arg=='-q':
        FAST = True 
    else:
        limit[arg[1:]] = float(opt)

if base_url == None:
    print "need url."
    print help
    exit(2)

for web_name,web_conf in re_conf.items():
    if(base_url.find(web_conf['key_word'])!=-1):
        g_source = web_name
        conf = web_conf
        break

if conf == None:
    print "has no conf for ",base_url
    exit(3)

        

header = ['数据采集时间','数据来源','品牌','名称','编号','价格','尺寸','产品配置汇总','促销信息','评论总数']
out_file = open('data_list.csv','w+')
out_file.write((','.join(header)+'\n').decode('utf-8').encode('gbk'))

data_list = spider(base_url,limit) 

print 'save to data_list.csv...'
for data in data_list:
    try:
        out_file.write((','.join(data)+'\n').decode('utf-8').encode('gbk'))
    except:
        print (','.join(data)+'\n')
        exit(0)
out_file.close()
print 'done.'
os.system("pause")
