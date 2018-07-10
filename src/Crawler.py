import urllib.request
import urllib.error
import re
import urllib
import socket

TAG_NAME='java'

#获取URL
decoding_tag_name=''
for i in TAG_NAME:                       #get decoding tag name
    if i=='+':
        decoding_tag_name+='%%2b'        # %2b代表'+'，第一个%用于转义
    else:
        decoding_tag_name+=i
URL='https://stackoverflow.com/questions/tagged/%s?page=%%d&sort=newest&pagesize=50'% decoding_tag_name
print(URL)

#获取总页数
page_code=''
try:
    request = urllib.request.Request(URL % (1))
    request.add_header("User-Agent", "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)")
    response = urllib.request.urlopen(request, timeout=10)
except urllib.error.HTTPError as e:
    print('【HTTP ERROR】')
except urllib.error.URLError as e:
    print('【URL ERROR】')
except socket.timeout as e:
    print('【TIMEOUT ERROR】')
except Exception as e:
    print('【Unknown ERROR】')
else:
    page_code = response.read().decode("utf-8")
page_num_span_pattern=re.compile('<span class="page-numbers">.*?</span>')
page_num_span=page_num_span_pattern.findall(page_code)
number_pattern=re.compile('[0-9]+')
total_num_str=number_pattern.findall(page_num_span[-1])
TOTAL_PAGE_NUM=int(total_num_str[0])
print(TOTAL_PAGE_NUM)






