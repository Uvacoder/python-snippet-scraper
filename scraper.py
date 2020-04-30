from bs4 import BeautifulSoup
import requests
import pymysql
import threading
import time

# gLock = threading.Lock()
# define the function that used for inserting the data into the database
def getCaseDetails(case_year, division_code, case_id):

    try:  
        # deifne the lock for the thread
        # gLock.acquire()

        item = str(case_year + division_code + case_id)
    
        url = 'https://courtlink.lexisnexis.com/cookcounty/FindDock.aspx?NCase='+ item + '&SearchType=0&Database=4&case_no=&PLtype=1&sname=&CDate='
        
        # use the ip proxy from crawlera
        response = requests.get(
            url,
            proxies={
                "http": "http://ff42eacc69c9495bb5cb7df4d7177a6a:@proxy.crawlera.com:8010/",
            },
        )
       
        html = response.content                
        
        # use the parser with lxml
        bs = BeautifulSoup(html,"lxml")

        # case number impoiert ethe lasdf
        case_number = bs.find_all('span',attrs={'id':'lblBottom'})[0].string

        # plaintiff
        tr = bs.find_all('tr',limit=5)[4]
        plaintiff = tr.find_all('td')[0].string

        # defendant
        defendant_ori = []
        tbd = bs.find_all('tbody',limit=3)[1]
        tr2s = tbd.find_all('tr')
        list_tr2s = list(tr2s)

        for index in range(len(list_tr2s)):
            if list_tr2s[index].find_all('td')[0].string == 'Defendant(s)': 
                defendant_ori.append(list_tr2s[index+1].find_all('td')[0].string)
                if (len(list_tr2s[index+2:])) != 0:
                    for i in (list_tr2s[index+2:]):
                        if i.find_all('td')[0].string != None:
                            defendant_ori.append(str(i.find_all('td')[0].string))
                    # for index2 in range(len(list_tr2s[index+1:])):
                    
                        # print(list_tr2s[index2].find_all('td')[0].string)           
        defendant = str(defendant_ori)

        # filling date
        tr3 = bs.find_all('tr',limit=1)[0]
        td3 = tr3.find_all('td')[0].string
        filling_date = td3[14:]
        
        # define the databse
        conn = pymysql.connect(host='localhost',user='root',password='82829576',database='scraper',port=3306)

        cursor = conn.cursor()
        
        # fill with the sql 
        sql = """ 
        insert into result(case_number,plaintiff,defendant,filling_date) values(%s,%s,%s,%s)
        """

        cursor.execute(sql,(case_number,plaintiff,defendant,filling_date))

        conn.commit()

        conn.close()
        # release the lock
        # gLock.release()
          
    except:
        
        print('this page does not exist' )

# define the automated function
def multi_thread():
    for i in range(400,900):
        # asynchronous process:
        task1 = threading.Thread(target=getCaseDetails, args=('1998','D',str(i).zfill(6)))
        task2 = threading.Thread(target=getCaseDetails, args=('1999','D',str(i).zfill(6)))
        task1.start()  
        task2.start() 


# run the function to scrape the date from the task page
if __name__ == '__main__':

    multi_thread()