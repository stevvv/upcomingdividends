'''
get dividents upcoming
lopez.steven01@gmail.com
'''
from nsetools import Nse
import time
nse = Nse()

def timeit(method):
    def timed(*args, **kw):
        print("Started executing function:%s" % method.__name__)
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        print('%r  %2.2f s' % (method.__name__, (te - ts)))
        return result

    return timed

def get_soup():
    from bs4 import BeautifulSoup
    import requests
    URL = 'https://www.moneycontrol.com/stocks/marketinfo/dividends_declared/index.php'
    # Make a GET request to fetch the raw HTML content
    html_content = requests.get(URL).text
    # Parse HTML code for the entire site
    soup = BeautifulSoup(html_content, "lxml")
    gdp = soup.find_all("table", attrs={"class": "b_12 dvdtbl"})
    return gdp
    
def scrape_table(gdp):
    import re
    # Lets go ahead and scrape first table with HTML code gdp[0]
    table1 = gdp[0]
    # the head will form our column names
    body = table1.find_all("tr")
    # Head values (Column names) are the first items of the body list
    head = body[0] # 0th item is the header row
    return body[1:] # All other items becomes the rest of the rows
    #body_rows

def get_rows(body_rows):
    import re
    all_rows = [] # will be a list for list for all rows
    code = []
    for row_num in range(1,len(body_rows)): # A row at a time
        row = [] # this will old entries for one row
        code.append(str(body_rows[row_num].find_all("td")[0]).split('=')[-1].split('"')[1].split('/')[-1])
        for row_item in body_rows[row_num].find_all("td"): #loop through all row entries
            # row_item.text removes the tags from the entries
            # the following regex is to remove \xa0 and \n and comma from row_item.text
            # xa0 encodes the flag, \n is the newline and comma separates thousands in numbers
            aa = re.sub("(\xa0)|(\n)|,","",row_item.text)
            #append aa to row - note one row entry is being appended
            row.append(aa)
        # append one row to all_rows
        all_rows.append(row)
    return code, all_rows

def gather_data(code, all_rows):
    import pandas as pd
    import numpy as np
    headings= ['Company', 'Type', 'Percent', 'Anounce', 'Record', 'ExDiv']
    from datetime import datetime
    df = pd.DataFrame(data=all_rows,columns=headings)
    df['ExDiv'] = pd.to_datetime(df['ExDiv'], dayfirst=True, errors='coerce')
    #df['Anounce'] = pd.to_datetime(df['Anounce'], dayfirst=True, errors='coerce')
    df = df.drop(['Record','Percent', 'Anounce'], axis=1)
    df['Delta'] = df['ExDiv'] - pd.to_datetime(datetime.now()).normalize()
    df['code'] = np.array(code)
    df = df[df.Delta >= pd.Timedelta(0, unit='D')]
    df['Div_LTP']=df.code.apply(lambda x: getDiv(x))
    df = df.drop('code', axis=1)
    return df

def getDiv(code):
    if nse.is_valid_code(code):
        tmp = nse.get_quote(code)
        return tmp.get('purpose').split('-')[-1].strip(),tmp.get('lastPrice')
    else:
        return ' '
    
        
@timeit
def main():
    from emailing import my_email
    gdp = get_soup()
    body_rows = scrape_table(gdp)
    code, all_rows = get_rows(body_rows)
    df  = gather_data(code, all_rows)
    #output(df, op)
    recievers = ##[list of emails]
    message = df.to_html(index=False, border=2, justify='left').replace('\n', '')
    my_email(recievers, 'Upcoming Dividend', message)
    #df.to_html(index=False)
main()
