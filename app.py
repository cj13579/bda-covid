import requests
from requests_file import FileAdapter
from bs4 import BeautifulSoup
import re
import datetime
import os
import pandas as pd

def getDailyRelease(day, month, year):

    # gets the data from the html file if it exists and returns a content object
    # otherwise returns None

    home = os.path.join(os.getcwd(), 'src')
    file = "covid-19-daily-release-{}-{}-{}".format(day, month, year)
    s = requests.Session()
    s.mount('file://', FileAdapter())
    r = s.get('file://{}/{}'.format(home, file))

    if r.status_code == 200: 
        return r.content

    file = "covid-19-update-minister-healths-remarks-{}-{}-{}".format(day, month, year)
    s = requests.Session()
    s.mount('file://', FileAdapter())
    r = s.get('file://{}/{}'.format(home, file))

    if r.status_code == 200: 
        return r.content        

    return None

def calculateRollingAverage(window_size, df, index_key):
    df['7 day rolling average'] = df.iloc[:,1].rolling(window=window_size).mean()
    df.set_index(index_key)
    return df

# only working on 2021 data
y =2021
c=0
pc=0

# create empty lists for appending the data to
positive_cases = []
positivity_rate = []
active_cases = []

for m in range(1,13):
    month = datetime.date(y,m,1).strftime('%B').lower()
    for i in range(1,32):
        try:
            date = datetime.date(y,m,i)
        except Exception as e:
            date = datetime.date(2099,12,31)

        if date <= datetime.date.today():
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

            # else:
                # print('No data available for {} {}'.format(str(i), month))

# save the data off for later and calculate rolling averages
if len(positive_cases)>6:
    df = pd.DataFrame(positive_cases)
    df = calculateRollingAverage(window_size=7,df=df,index_key='date')
    df.to_csv('html/csv/positive_cases.csv', index=False)
    print(df.iloc[[-1]])
    
if len(positivity_rate)>6:
    df = pd.DataFrame(positivity_rate)
    df = calculateRollingAverage(window_size=7,df=df,index_key='date')
    df.to_csv('html/csv/positivity_rate.csv', index=False)
    print(df.iloc[[-1]])

if len(active_cases)>6:
    df = pd.DataFrame(active_cases)
    df = calculateRollingAverage(window_size=7,df=df,index_key='date')
    df.to_csv('html/csv/active_cases.csv', index=False)
    print(df.iloc[[-1]])


# c is a count of the days that we did stuff for
print(c)

# pc is a count of the days that we got positve a counts
# this is a proxy for how many days there was some kind of statement
# some may contain more than one day's data
print(pc)
