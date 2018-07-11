import urllib.request
import urllib.error
import re
import urllib
import socket
import sqlite3
import time
number_pattern=re.compile('[0-9]+')
success_question_num=0
fail_question_num=0

TAG_NAME='c++'

#获取URL
encoding_tag_name=''
for i in TAG_NAME:                       #get decoding tag name
    if i=='+':
        encoding_tag_name+='%%2b'        # %2b代表'+'，第一个%用于转义
    else:
        encoding_tag_name+=i
URL='https://stackoverflow.com/questions/tagged/%s?page=%%d&sort=newest&pagesize=50'% encoding_tag_name
print(URL % 1)

#获取总页数
page_code=''
try:
    request = urllib.request.Request(URL % (1))
    request.add_header("User-Agent", "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)")
    response = urllib.request.urlopen(request, timeout=20)
except urllib.error.HTTPError:
    print('【HTTP ERROR】')
    exit()
except urllib.error.URLError:
    print('【URL ERROR】')
except socket.timeout:
    print('【TIMEOUT ERROR】')
except Exception:
    print('【Unknown ERROR】')
else:
    page_code = response.read().decode("utf-8")
page_num_span_pattern=re.compile('<span class="page-numbers">.*?</span>')
page_num_span=page_num_span_pattern.findall(page_code)
total_num_str=number_pattern.findall(page_num_span[-1])
TOTAL_PAGE_NUM=int(total_num_str[0])
print(TOTAL_PAGE_NUM)

#TOTAL_PAGE_NUM=5       #!!! For testing  !!!

#将所有的id存放到数据库中
question_page_pattern=re.compile('"question-summary-[0-9]+"')
question_db = sqlite3.connect('question.db')
print('connect successfully')
cursor=question_db.cursor()
try:
    cursor.execute('CREATE TABLE QUESTION (ID INT PRIMARY KEY  NOT NULL);')
except sqlite3.OperationalError:
    print('table exist')
page_num=TOTAL_PAGE_NUM+1
http_error_num=0
while page_num>1:
    if page_num % 100 ==0:
        time.sleep(1)
    page_num-=1
    url = URL % page_num
    try:
        request = urllib.request.Request(url)
        request.add_header("User-Agent", "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)")
        response = urllib.request.urlopen(request, timeout=10)
    except urllib.error.HTTPError:
        page_num+=1
        http_error_num+=1
        print('【HTTP ERROR】,begin to sleep %d seconds' % (2**(http_error_num+2)))
        time.sleep(2**(http_error_num+2))
        continue
    except urllib.error.URLError:
        print('【URL ERROR】')
        print(url)
        continue
    except socket.timeout:
        print('【TIMEOUT ERROR】')
        continue
    except Exception:
        print('【Unknown ERROR】')
        continue
    else:
        http_error_num=0
        page_code = response.read().decode("utf-8")
        raw_id_str=question_page_pattern.findall(page_code)
        for str in raw_id_str:
            id_str=number_pattern.findall(str)
            id=int(id_str[0])
            try:
                cursor.execute("INSERT INTO QUESTION (ID)  VALUES (%d)" % id);
            except sqlite3.IntegrityError:
                print('exist %d' % id)
                fail_question_num+=1
                continue
            else:
                success_question_num+=1
    print('page num= %d' % (TOTAL_PAGE_NUM - page_num + 1))
    question_db.commit()
question_db.close()
print('succ = %d' % success_question_num)
print('fail = %d' % fail_question_num)
