import requests
from requests_file import FileAdapter
from bs4 import BeautifulSoup
import re
import datetime
import pandas as pd
from os import listdir, getcwd, path, mkdir, name
import git

source = path.join(getcwd(), 'src')
if not path.exists(source):
    mkdir(source)

def downloadFiles():
    print("Downloading data...")
    y=2021
    for m in range(1,13):
        month = datetime.date(y,m,1).strftime('%B').lower()
        for i in range(1,32):

            found=False
            # don't download files that we already have 
            # probably more efficient to load this into a list once but, watevs
            pattern = re.compile(".*covid-19.*-{}-{}-{}".format(i,month,y))

            for filepath in listdir(source):
                if pattern.match(filepath):
                    print("Already have data for {} {} {}".format(i,month,y))
                    found = True
                    break
            if found:
                continue
        
            # check if the date is a valid date. do this cos im just iterating ha
            try:
                date = datetime.date(y,m,i)
            except Exception as e:
                date = datetime.date(2099,12,31)

            # if its a valid date and its less than or equal to today then do something
            if date <= datetime.date.today():

                # tell the world
                print("Getting data for {} {} {}".format(i, month, y))

                url = 'https://www.gov.bm/articles/covid-19-daily-release-{}-{}-{}'.format(i, month, y)
                r = requests.get(url)
                if r.status_code == 200: 
                    htmlfile = path.join(source,'covid-19-daily-release-{}-{}-{}.html'.format(str(i),month,str(y)))

                    with open(htmlfile, 'wb') as file:
                        file.write(r.content)
                    print("Retrieved data for {} {} {}".format(i, month, y))
                    continue
                else:
                    url = 'https://www.gov.bm/articles/covid-19-update-minister-healths-remarks-{}-{}-{}'.format(i,month,y)
                    r = requests.get(url)
                    if r.status_code == 200:
                        htmlfile = path.join(source,'covid-19-update-minister-healths-remarks-{}-{}-{}.html'.format(str(i),month,str(y)) )
                        with open(htmlfile, 'wb') as file:
                            file.write(r.content)
                        print("Retrieved data for {} {} {}".format(i, month, y))
                        continue
                
                # if we get here we didn't find data for this day
                print("No data available for {} {} {}". format(i, month, y))

def commitAndPush():

    repo = git.Repo(getcwd())
    for item in repo.index.diff(None):
        if 'csv' in item.a_path:
            repo.index.add([item.a_path])

    date = datetime.date.today().strftime("%d%B%Y")
    commit_msg = "Add data from {}".format(date)
    repo.index.commit(commit_msg)
    origin = repo.remotes['origin']
    origin.push()

def getDailyRelease(day, month, year):

    # gets the data from the html file if it exists and returns a content object
    # otherwise returns None

    home = getcwd()
    home = home.replace('\\','/')
    file = "src/covid-19-daily-release-{}-{}-{}.html".format(day, month, year)
    s = requests.Session()
    if name == 'nt':
        s.mount('file://', FileAdapter())
        r = s.get('file:///{}/{}'.format(home, file))
    else:
        s.mount('file://', FileAdapter())
        r = s.get('file://{}/{}'.format(home, file))
    

    if r.status_code == 200: 
        return r.content

    file = "src/covid-19-update-minister-healths-remarks-{}-{}-{}.html".format(day, month, year)
    s = requests.Session()

    if name == 'nt':
        s.mount('file://', FileAdapter())
        r = s.get('file:///{}/{}'.format(home, file))
    else:
        s.mount('file://', FileAdapter())
        r = s.get('file://{}/{}'.format(home, file))

    if r.status_code == 200: 
        return r.content        

    return None

def calculateRollingAverage(window_size, df, index_key):
    df['7 day rolling average'] = df.iloc[:,1].rolling(window=window_size).mean()
    df.set_index(index_key)
    return df

def htmlToCsv():
    # only working on 2021 data
    y =2021
    # create empty lists for appending the data to
    positive_cases = []
    positivity_rate = []
    active_cases = []
    c=0
    pc=0
    print("Converting HTML to CSV")
    for m in range(1,13):
        month = datetime.date(y,m,1).strftime('%B').lower()
        for i in range(1,32):
            try:
                date = datetime.date(y,m,i)
            except:
                date = datetime.date(2099,12,31)

            if date <= datetime.date.today():
                print("Checking if there is data for {} {} {}".format(i, month, y))
                data = getDailyRelease(str(i), month, str(y))

                if data:
                    c=c+1
                    found = False
                    soup = BeautifulSoup(data, "html.parser")
                    for p in soup.find_all("p"):
                        if p.text:
                            #results &positive
                            results_match = '.*\s(?P<results>\d+).*test\sresults.*'
                            if re.match(results_match, p.text):
                                match = re.match(results_match, p.text)
                                results = int(match.group('results'))


                                #positive
                                positive = None
                                digits_pos = '.*received\s(?P<results>\d+).*test\sresults.*and\s(?P<positive>\d+)\s[were|was].*positive.*'
                                words_pos = '.*\s(?P<results>\d+)\stest\sresults.*\,\sand\s(?P<positive>[one|two|three|four|five|six|seven|eight|nine]+).*[were|was]\spositive.*'

                                if re.match(digits_pos, p.text):
                                    match = re.match(digits_pos, p.text)
                                    positive = int(match.group('positive'))
                                
                                if positive is None:
                                    if re.match(words_pos, p.text):
                                        match = re.match(words_pos, p.text)
                                        pw = match.group('positive')
                                        
                                        if pw == 'one':
                                            positive=1

                                        if pw == 'two':
                                            positive=2

                                        if pw == 'three':
                                            positive=3

                                        if pw == 'four':
                                            positive=4

                                        if pw == 'five':
                                            positive=5

                                        if pw == 'six':
                                            positive=6

                                        if pw == 'seven':
                                            positive=7

                                        if pw == 'eight':
                                            positive=8

                                        if pw == 'nine':
                                            positive=9

                                
                                if positive:
                                    pos_rate = (positive / results) *100
                                    positive_cases.append({
                                        'date':date,
                                        'Positive Cases': positive
                                    })
                                    positivity_rate.append({'date':date, 'Positivity Rate':pos_rate})
                                    pc = pc+1
                                found = True
                                # print('The positivity rate was {}% on {} {}'.format(str(pos_rate), str(i), month))
                            


                            #deaths
                            #active cases
                            
                            if re.match('.*\s(?P<active>\d+)\sactive\scases.*',p.text):
                                match = re.match('.*\s(?P<active>\d+)\sactive\scases.*',p.text)
                                active = match.group('active')
                                active_cases.append({
                                    'date':date,
                                    'Active Cases':int(active)
                                    })

                                # print('There were {} active cases on {} {}'.format(str(active), str(i), month))
                                found = True
                    if not found:
                        print("Press release found for {}-{}-{} but didn't find active case numbers.".format(str(i),month,str(y)))
                else:
                    print('No data available for {} {}'.format(str(i), month))
    # save the data off for later and calculate rolling averages
    if len(positive_cases)>6:
        df = pd.DataFrame(positive_cases)
        df = calculateRollingAverage(window_size=7,df=df,index_key='date')
        csv = path.join(getcwd(),'csv','positive_cases.csv')
        df.to_csv(csv, index=False)
        print(df.iloc[[-1]])
        
    if len(positivity_rate)>6:
        df = pd.DataFrame(positivity_rate)
        df = calculateRollingAverage(window_size=7,df=df,index_key='date')
        csv = path.join(getcwd(),'csv','positivity_rate.csv')
        df.to_csv(csv, index=False)
        print(df.iloc[[-1]])

    if len(active_cases)>6:
        df = pd.DataFrame(active_cases)
        df = calculateRollingAverage(window_size=7,df=df,index_key='date')
        csv = path.join(getcwd(),'csv','active_cases.csv')
        df.to_csv(csv, index=False)
        print(df.iloc[[-1]])

    # c is a count of the days that we did stuff for
    print(c)

    # pc is a count of the days that we got positve a counts
    # this is a proxy for how many days there was some kind of statement
    # some may contain more than one day's data
    print(pc)

try:
    # downloadFiles()
    # htmlToCsv()
    commitAndPush()
except Exception as e:
    print("Error occurred. Error was {}".format(e))