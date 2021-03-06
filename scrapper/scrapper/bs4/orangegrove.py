from builtins import range

from bs4 import BeautifulSoup as BS
import requests
import mysql.connector
import datetime
import math

from sqlalchemy import false

domain = 'https://florida.theorangegrove.org/'

mydb=mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="oerintegrationdb"
    )

myac=mydb.cursor()

#------------------- TO get Row from DB ---------------------
'''
myac.execute('select * from triplesOG where predicate = "hasRaw"')
rows = myac.fetchall()

for r in rows:
    metadata_tb = BS(r[3],'html.parser')
    for p in metadata_tb.find_all('p'):
        print(p.get_text())
    exit()
'''

subjRepository = 'Rep1'

#Insert Repository
'''
sql = "INSERT INTO triplesOG(subject, predicate, object, time_date) VALUES(%s,%s,%s,%s)"
values = (subjRepository,'hasName','The Orange Grove',datetime.datetime.now())
myac.execute(sql,values)
mydb.commit()
sql = "INSERT INTO triplesOG(subject, predicate, object, time_date) VALUES(%s,%s,%s,%s)"
values = (subjRepository,'hasUrl','https://florida.theorangegrove.org/og/hierarchy.do?topic=16fd73ce-64e0-6992-b704-d73a2763d9e7&page=1',datetime.datetime.now())
myac.execute(sql,values)
mydb.commit()
'''

#Find list of subjects pages
subjectRow = [
    ['og/hierarchy.do?topic=612a768f-4979-aa54-68ec-09affba54d09','K-12 Open Textbooks',90],
    ['og/hierarchy.do?topic=acedc05e-0d93-f56d-0034-a70d3546f5e0','OGT+ Print on Demand Books',101],
    ['og/hierarchy.do?topic=e17ea474-21cd-d407-9165-bbbc165884b4','WebAssign Supported Textbooks ',4],
    ['og/hierarchy.do?topic=0fd16144-0047-7064-ab78-1169c0cd3683','InTech',4799],
    ['og/hierarchy.do?topic=94c81979-5a4a-0e4c-f678-458e8d4aa9b8','Open Course Library',39],
    ['og/hierarchy.do?topic=b1530c9e-c5d9-cf13-e5f9-2a6391a2b163','Saylor Fundation',4],
]

for x in subjectRow:

    subjCategory = '{0}{1}'.format('category',list(subjectRow).index(x)+1)
    sql = "INSERT INTO triplesOG(subject, predicate, object, time_date) VALUES(%s,%s,%s,%s)"
    values = (subjRepository, 'hasSubject', subjCategory, datetime.datetime.now())
    myac.execute(sql, values)
    mydb.commit()
    print('\nSaving Cat: {0}'.format(x[1]))

    sql = "INSERT INTO triplesOG(subject, predicate, object, time_date) VALUES(%s,%s,%s,%s)"
    values = (subjCategory, 'hasName', x[1], datetime.datetime.now())
    myac.execute(sql, values)
    mydb.commit()

    #calculando numero de iteraciones
    numIterate = math.ceil(x[2] / 10)
    for i in range(numIterate):
        # download page of TB
        web_og = requests.get('{0}{1}&page={2}'.format(domain, x[0],i+1))
        raw_og = web_og.content
        soup_og = BS(raw_og, 'html.parser')
        box_results = soup_og.find('div',{'id':'searchresults'})
        titles_tb = box_results.find_all('a',{'class':'titlelink'})
        for a in titles_tb:
            url_tb = a.get('href')
            print(a.get_text())
            #Descargando RAW TB
            web_tb = requests.get('{0}{1}'.format(domain, url_tb[1:]))
            raw_tb = web_tb.content
            soup_tb = BS(raw_tb, 'html.parser')
            raw_data = soup_tb.find('div',{'class':'area'})

            #Savig RAW
            sql = "INSERT INTO triplesOG(subject, predicate, object, time_date, process) VALUES(%s,%s,%s,%s,%s)"
            values = (subjCategory, 'hasRaw', str(raw_data), datetime.datetime.now(),False)
            myac.execute(sql, values)
            mydb.commit()
        print('\t\tIterate {0} / {1}'.format(i+1,numIterate))
    print('END CAT')