#coding=utf-8
import getopt,sys,urllib2,re,os,time,json,HTMLParser
from selenium import webdriver
reload(sys)
sys.setdefaultencoding('utf-8')
'''
driver = webdriver.PhantomJS()

driver.get('http://item.jd.com/1027344.html')
data = driver.find_element_by_id('jd-price').text
print data
'''
help = '''usage:
python ./spider.py -u base_url 
    -u: base_url.
'''
try:
    args,opts = getopt.getopt(sys.argv[1:],"u:h")
except:
    print "invalid args."
    print help
    exit(1)


re_conf = {'京东':{},'苏宁':{}}

suning_conf = re_conf['苏宁']
jd_conf = re_conf['京东']

jd_conf['key_word'] = 'jd.com'
jd_conf['brand'] = []
jd_conf['brand'].append(re.compile("<li>品牌：<a.*>(.*)</a></li>"))
jd_conf['name']  = []
jd_conf['name'].append(re.compile("商品名称：(.*)</li>"))
jd_conf['NO']    = []
jd_conf['NO'].append(re.compile("商品编号：(.*)</li>"))

suning_conf['key_word'] = 'suning.com'


conf = None

brand_re = re.compile("<li>品牌：<a.*>(.*)</a></li>")
name_re = re.compile("商品名称：(.*)</li>")
NO_re = re.compile("商品编号：(.*)</li>")
price_base_url = 'http://p.3.cn/prices/get?skuid=J_'
size_re = re.compile("尺寸：(.*)</li>")
size2_re = re.compile("屏幕尺寸</td><td>([^<]*)</td>")
size3_re = re.compile("title>.*([\d\.]+英寸).*</title>")
conf_re = re.compile("title>.*(?:（|\()(.*)(?:）|\)).*</title>")
time = time.strftime('%Y-%m-%d %H:%M:%S')

html_parser = HTMLParser.HTMLParser()

g_source = None


def get_item_data(url):
    
    print url
    try:
        data = urllib2.urlopen(url)
        data = data.read().decode('gbk').encode('utf-8')
    except Exception,e:
        print "net error on item ",url,e
        return None
    try:
        brand = brand_re.findall(data)[0]
        name = name_re.findall(data)[0]
        NO = NO_re.findall(data)[0]
        size = size_re.findall(data)
        if len(size)>0:
            size = size[0]
        else:
            size = size2_re.findall(data)
            if len(size)>0:
                size = size[0]
            else:
                size = size3_re.findall(data)[0]
        conf = conf_re.findall(data)[0]
    except:
        print 'error'
        return None

    price = urllib2.urlopen(price_base_url+NO)
    price = json.loads(price.read())[0]['p'].encode('utf-8')
    return (time,'京东',brand,name,NO,price,size,conf)

    
    
def spider(url,limit):
    next_page_url = url
    base_url = "http://list.jd.com/list.html" 
    page_re  = re.compile(r"<a href=\\\"([^>]*)\\\" class=\\\"next\\\">下一页.*")
    item_re  = re.compile(r"class=\\\"p-img\\\"><a target=\\\"_blank\\\" href=\\\"([^>]*)\\\"><img")
    res = []
    while next_page_url != None:
        print next_page_url,'...'
        try:
            data = urllib2.urlopen(next_page_url)
            data = data.read()
        except Exception,e:
            print "net error on",next_page_url,"page:",e
            continue 


        item_list = item_re.findall(data)
        for item_url in item_list:
            item_data = get_item_data(item_url)
            if item_data != None:
                res.append(item_data)

        tmp = next_page_url
        next_page_url = None
        tmp_url = page_re.findall(data)
        if len(tmp_url) > 0:
            next_page_url = base_url+html_parser.unescape(tmp_url[0])

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

        

header = ['监测时间','网上商城','品牌','名称','编号','价格','尺寸','产品配置汇总','促销','评论数']
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
