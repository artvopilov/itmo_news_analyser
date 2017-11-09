from bs4 import BeautifulSoup
import requests
from sqlalchemy.orm import sessionmaker
from bottle import route, run, template, request, redirect, static_file
from sqlalchemy import create_engine
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from math import log2
import pickle
import os


url = "https://news.ycombinator.com/news"


def get_news(url):
    result_list = []
    row_dict = {}
    html_code = requests.get(url).text
    read_html = BeautifulSoup(html_code, "html5lib")
    work_table = read_html.table.findAll('table')[1]
    tbl_rows = work_table.tbody.findAll('tr')
    for tr in tbl_rows:
        attrs_dict = tr.attrs
        if 'class' in attrs_dict:
            if tr['class'] == ["morespace"]:
                break
            elif tr['class'] == ["athing"]:
                row_dict['title'] = tr.findAll('td')[2].a.text
                row_dict['url'] = tr.findAll('td')[2].a['href']
            elif tr['class'] == ["spacer"]:
                result_list.append(row_dict)
                row_dict = {}
        else:
            if 'class' in tr.findAll('td')[1].findAll('span')[0].attrs:
                if tr.findAll('td')[1].span['class'] == ['score']:
                    row_dict['points'] = tr.findAll('td')[1].span.text.split()[0]
                    row_dict['author'] = tr.findAll('td')[1].a.text
                    row_dict['comments'] = tr.findAll('td')[1].findAll('a')[-1].text
                    if row_dict['comments'] != 'discuss':
                        row_dict['comments'] = row_dict['comments'].split()[0]
                else:
                    row_dict['author'] = 'Unknown'
                    row_dict['points'] = 0
                    row_dict['comments'] = 0
            else:
                row_dict['author'] = 'Unknown'
                row_dict['points'] = 0
                row_dict['comments'] = 0
    return result_list


Base = declarative_base()


class News(Base):
    __tablename__ = "news"
    id = Column(Integer, primary_key = True)
    title = Column(String)
    author = Column(String)
    url = Column(String)
    comments = Column(Integer)
    points = Column(Integer)
    label = Column(String)


engine = create_engine("sqlite:///news.db")
Base.metadata.create_all(bind=engine)


session = sessionmaker(bind=engine)
s = session()


def add30news():
    for each_d in get_news(url):
        news = News(title = each_d['title'],
                    author = each_d['author'],
                    url = each_d['url'],
                    comments = each_d['comments'],
                    points = each_d['points'])
        s.add(news)
        s.commit()


color_dict = {'never': 'lightblue',
              'maybe': '#ffffcc',
              'good': ' #b3ffb3'}


@route('/')
@route('/news')
def news_list():
    fortemp_list = []
    """makeadd_clsses()"""
    with open('pickle.txt', 'rb') as file:
        d_classes = pickle.load(file)
    num_cl, num_uw = 0, 0
    for c in d_classes.keys():
        num_cl += d_classes[c][0]
        print('How many', d_classes[c][0], c)
        num_uw += len(d_classes[c][1].keys())
    print(num_uw)
    rows = s.query(News).filter(News.label == None).all()
    for row in rows:
        print(row.title)
        rez_d = {}
        for class1 in ['maybe', 'good', 'never']:
            word_sum = sum(d_classes[class1][1][wrd] for wrd in d_classes[class1][1].keys())
            r = 0
            print(class1, 'word_sum', word_sum, 'word_sum+num_uw', word_sum + num_uw)
            words_list = change_str(row.title)
            words_list.append(row.author)
            for word in words_list:
                r += log2((d_classes[class1][1].get(word, 0) + 1) / (num_uw + word_sum))
                print(word, (d_classes[class1][1].get(word, 0) + 1), 'log', log2((d_classes[class1][1].get(word, 0) + 1) / (num_uw + word_sum)))
            r += log2(d_classes[class1][0] / num_cl)
            print('frequency_class', class1, log2(d_classes[class1][0] / num_cl))
            print('aftall', r)
            rez_d[class1] = r
        cll = max(rez_d.keys(), key = lambda x: rez_d[x])
        print(cll)
        print('rez', rez_d)
        fortemp_list.append((row, color_dict[cll]))
    fortemp_list.sort(key=lambda x: x[1])
    return template('news_template', rows=fortemp_list)



@route('/add_label')
def get_label():
    inf = request.query.dict
    label = inf['label'][0]
    id = int(inf['id'][0])
    row = s.query(News).filter(News.id == id).first()
    row.label = label
    s.commit()
    add_to_clsses(row)
    redirect('/news')


@route('/update_news')
def update():
    news_list = get_news(url)
    for new in news_list:
        if (s.query(News).filter(News.title == new['title']).first()) and \
                (s.query(News).filter(News.author == new['author']).first()):
            continue
        else:
            neww = News(title=new['title'],
                        author=new['author'],
                        url=new['url'],
                        comments=new['comments'],
                        points=new['points'])
            s.add(neww)
            s.commit()
    redirect('/news')


@route('/<filename>')
def st_fl(filename):
    return static_file(filename, root="./")


def change_str(string):
    rez_list = []
    string = string.lower()
    for word in string.split():
        if word in '“”;:?!,.–-()[]':
            continue
        word = word.strip('”“`;–:?!,.-()[]')
        rez_list.append(word)
    return rez_list


def add_to_clsses(row):
    if os.path.isfile('pickle.txt'):
            with open('pickle.txt', 'rb') as file:
                doc_class_dict = pickle.load(file)
    else:
        doc_class_dict = {}
    if row.label in doc_class_dict:
        doc_class_dict[row.label][0] += 1
    else:
        doc_class_dict[row.label] = []
        doc_class_dict[row.label].append(1)
        doc_class_dict[row.label].append({})
    words_list = change_str(row.title)
    words_list.append(row.author)
    for word in words_list:
        if word in doc_class_dict[row.label][1]:
            doc_class_dict[row.label][1][word] += 1
        else:
            doc_class_dict[row.label][1][word] = 1

    with open('pickle.txt', 'wb') as file:
        pickle.dump(doc_class_dict, file)


def make_classes():
    doc_class_dict = {}
    rows = s.query(News).filter(News.label != None).all()
    for row in rows:
        if row.label in doc_class_dict:
            doc_class_dict[row.label][0] += 1
        else:
            doc_class_dict[row.label] = []
            doc_class_dict[row.label].append(1)
            doc_class_dict[row.label].append({})
        words_list = change_str(row.title)
        words_list.append(row.author)
        for word in words_list:
            if word in doc_class_dict[row.label][1]:
                doc_class_dict[row.label][1][word] += 1
            else:
                doc_class_dict[row.label][1][word] = 1

    with open('pickle.txt', 'wb') as file:
        pickle.dump(doc_class_dict, file)


"""for each_d in get_news(url):    # Output func get_news()
    print('{', end='')
    for key in each_d.keys():
        print(key, ': ', each_d[key], ';')
    print('}')"""


if __name__ == '__main__':
    make_classes()
    run(host='localhost', port=8080)
