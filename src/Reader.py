import sqlite3

# db1.db : question tagged c++ , totally 577,258 questions
# db2.db : question tagged c++ && (sorting || search || tree || graph || linked-list) , totally 9,496 questions
DB_NAME = 'db2.db'
URL_HEAD = 'https://stackoverflow.com/questions/'

if __name__ == '__main__':
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    print('Connect to database %s successfully.' % DB_NAME)
    data = cursor.execute("SELECT ID  from QUESTION")
    count = 0
    for row in data:
        question_id = row[0]
        url = URL_HEAD + str(question_id)
        count += 1
        # using url here
        print(url)
    conn.close()
    print('Connect close successfully , totally %d links.' % count)
