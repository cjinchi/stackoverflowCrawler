import urllib.request
import urllib.error
import re
import urllib
import socket
import sqlite3
import time

NUMBER_PATTERN = re.compile('[0-9]+')


def get_url_form_by_tag(tag_name):
    encoding_tag_name = ''
    for i in tag_name:  # get decoding tag name
        if i == '+':
            encoding_tag_name += '%%2b'  # %2b代表'+'，第一个%用于转义
        elif i == ' ':
            encoding_tag_name += '%%20'
        else:
            encoding_tag_name += i
    url = 'https://stackoverflow.com/questions/tagged/%s?page=%%d&sort=newest&pagesize=50' % encoding_tag_name
    return url


def get_total_page_num(url_form):
    page_code = ''
    try:
        request = urllib.request.Request(url_form % (1))
        request.add_header(
            "User-Agent",
            "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)")
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
    page_num_span_pattern = re.compile('<span class="page-numbers">.*?</span>')
    page_num_span = page_num_span_pattern.findall(page_code)
    total_num_str = NUMBER_PATTERN.findall(page_num_span[-1])
    total_page_num = int(total_num_str[0])
    return total_page_num


def save_ids(url_form, total_page_num):
    success_num = 0
    fail_num = 0
    question_page_pattern = re.compile('"question-summary-[0-9]+"')
    question_db = sqlite3.connect('question.db')
    print('connect successfully')
    cursor = question_db.cursor()
    try:
        cursor.execute('CREATE TABLE QUESTION (ID INT PRIMARY KEY  NOT NULL);')
    except sqlite3.OperationalError:
        print('table exist')
    page_num = total_page_num + 1
    http_error_num = 0
    while page_num > 1:
        if page_num % 100 == 0:
            time.sleep(1)
        page_num -= 1
        url = url_form % page_num
        try:
            request = urllib.request.Request(url)
            request.add_header(
                "User-Agent",
                "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)"
            )
            response = urllib.request.urlopen(request, timeout=10)
        except urllib.error.HTTPError:
            page_num += 1
            http_error_num += 1
            print('【HTTP ERROR】,begin to sleep %d seconds' %
                  (2**(http_error_num + 2)))
            time.sleep(2**(http_error_num + 2))
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
            http_error_num = 0
            page_code = response.read().decode("utf-8")
            raw_id_str = question_page_pattern.findall(page_code)
            for str in raw_id_str:
                id_str = NUMBER_PATTERN.findall(str)
                id = int(id_str[0])
                try:
                    cursor.execute(
                        "INSERT INTO QUESTION (ID)  VALUES (%d)" % id)
                except sqlite3.IntegrityError:
                    print('exist %d' % id)
                    fail_num += 1
                    continue
                else:
                    success_num += 1
        print('page num= %d' % (total_page_num - page_num + 1))
        question_db.commit()
    question_db.close()
    print('succ = %d' % success_num)
    print('fail = %d' % fail_num)


if __name__ == '__main__':
    url_form = get_url_form_by_tag('c++')
    print(url_form % 1)
    total_page_num = get_total_page_num(url_form)
    save_ids(url_form, total_page_num)
