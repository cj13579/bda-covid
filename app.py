import requests
from requests_file import FileAdapter
from bs4 import BeautifulSoup
import re
import datetime
import pandas as pd
from os import listdir, getcwd, path, mkdir, name, getenv
import git

# https://www.cia.gov/the-world-factbook/countries/bermuda/#people-and-society
population = 72084

source = path.join(getcwd(), 'src')
if not path.exists(source):
    mkdir(source)

def downloadFiles():
    print("Downloading data...")

    known_files = listdir(source)
    known_missing = []
    known_missing_csv = path.join(source,'known_missing.csv')
    if path.exists(known_missing_csv):
        origlist = pd.read_csv(known_missing_csv).values.tolist()
        for sublist in origlist:
            for item in sublist:
                known_missing.append(str(item))
        

    date = datetime.datetime(year=2021,month=1,day=1)

    while date <= date.today():

        i = date.day
        month = date.strftime('%B').lower()
        y = date.year
        found=False

        # check for known missing
        checker = date.strftime('%Y%m%d')
        if checker in known_missing:
            print("We know there is data missing for this date. Skipping {} {} {}".format(i,month,y))
            date = date + datetime.timedelta(days=1)
            continue

        # don't download files that we already have 
        # probably more efficient to load this into a list once but, watevs
        pattern = re.compile(".*covid-19.*-{}-{}-{}".format(i,month,y))

        for filepath in known_files:
            if pattern.match(filepath):
                print("Already have data for {} {} {}".format(i,month,y))
                found = True
                break

        if found:
            date = date + datetime.timedelta(days=1)
            continue


        # tell the world
        print("Getting data for {} {} {}".format(i, month, y))

        url = 'https://www.gov.bm/articles/covid-19-daily-release-{}-{}-{}'.format(i, month, y)
        r = requests.get(url)
        if r.status_code == 200: 
            htmlfile = path.join(source,'covid-19-daily-release-{}-{}-{}.html'.format(str(i),month,str(y)))

            with open(htmlfile, 'wb') as file:
                file.write(r.content)
            print("Retrieved data for {} {} {}".format(i, month, y))
            date = date + datetime.timedelta(days=1)
            continue

        url = 'https://www.gov.bm/articles/covid-19-update-minister-healths-remarks-{}-{}-{}'.format(i,month,y)
        r = requests.get(url)
        if r.status_code == 200:
            htmlfile = path.join(source,'covid-19-update-minister-healths-remarks-{}-{}-{}.html'.format(str(i),month,str(y)) )
            with open(htmlfile, 'wb') as file:
                file.write(r.content)
            print("Retrieved data for {} {} {}".format(i, month, y))
            date = date + datetime.timedelta(days=1)
            continue

        #variation on above url that's been seen
        url = 'https://www.gov.bm/articles/covid-19-update-minister-health-remarks-{}-{}-{}'.format(i,month,y)
        r = requests.get(url)
        if r.status_code == 200:
            htmlfile = path.join(source,'covid-19-update-minister-healths-remarks-{}-{}-{}.html'.format(str(i),month,str(y)) )
            with open(htmlfile, 'wb') as file:
                file.write(r.content)
            print("Retrieved data for {} {} {}".format(i, month, y))
            date = date + datetime.timedelta(days=1)
            continue
        
        todayminusthree = date + datetime.timedelta(days=3)
        if date <= todayminusthree:
            print("Didn't find data for old date. won't do this again")
            known_missing.append(date.strftime('%Y%m%d'))
            date = date + datetime.timedelta(days=1)
            continue

        # if we get here we didn't find data for this day
        print("No data available for {} {} {}. Will try again". format(i, month, y))
        date = date + datetime.timedelta(days=1)

    pd.DataFrame(known_missing).to_csv(known_missing_csv,index=None)

def commitAndPush():
    count = 0
    repo = git.Repo(getcwd())
    for item in repo.index.diff(None):
        if 'csv' in item.a_path:
            repo.index.add([item.a_path])
            count = count + 1

    if count > 0:
        date = datetime.date.today().strftime("%d%B%Y")
        commit_msg = "Add data from {}".format(date)
        repo.index.commit(commit_msg)
        origin = repo.remotes['origin']
        if not origin.push():
            print("Unable to send new data")
    else:
        print("No changes to push")

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

def calculateRollingAverage(window_size, df, col_to_roll):
    column_name = '{} day rolling average'.format(window_size)
    df[column_name] = df[col_to_roll].rolling(window=window_size).mean()
    
    return df

def calculateCasesPer100k(df, population):
    df['Cases per 100k'] = (df['7 day rolling average']/population)*100000
    return df

def htmlToCsv():
    # only working on 2021 data
    y =2021
    # create empty lists for appending the data to
    positive_cases = []
    positivity_rate = []
    active_cases = []
    case_breakdown = {}
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
                            imported = None
                            known_contact = None
                            unknown_contact = None
                            under_investigation = None

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

                                        if pw == 'none':
                                            positive=0
                                        
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
                                        # 'Test results received': results,    
                                        'Positive Cases': positive
                                    })
                                    positivity_rate.append({'date':date, 'Positivity Rate':pos_rate})
                                    pc = pc+1
                                found = True
                                # print('The positivity rate was {}% on {} {}'.format(str(pos_rate), str(i), month))
                            
                            #deaths
                            
                            #imported
                            if re.match('.*\s(?P<imported>\d+)\sare\sImported.*',p.text):
                                match = re.match('.*\s(?P<imported>\d+)\sare\sImported.*',p.text)
                                imported = match.group('imported')
                                try:
                                    case_breakdown[date].update({
                                        'date': date,
                                        'Imported': imported,
      
                                    })
                                except KeyError:
                                    case_breakdown[date] = {
                                        'date': date,
                                        'Imported': imported,
                                    }
                            # local transmission known contact
                            if re.match('.*\s(?P<localKnown>\d+)\sare\sLocal\stransmission\swith\sknown.*',p.text):
                                match = re.match('.*\s(?P<localKnown>\d+)\sare\sLocal\stransmission\swith\sknown.*',p.text)
                                known_contact = match.group('localKnown')
                                try:
                                    case_breakdown[date].update({
                                        'date': date,
                                        'Local - Known contact': known_contact,

                                    })
                                except KeyError:
                                    case_breakdown[date] = {
                                        'date': date,
                                        'Local - Known contact': known_contact,
                                    }

                            # local transmission unknown contact
                            if re.match('.*\s(?P<localUnknown>\d+)\sare\sLocal\stransmission\swith\san\sunknown.*',p.text):
                                match = re.match('.*\s(?P<localUnknown>\d+)\sare\sLocal\stransmission\swith\san\sunknown.*',p.text)
                                unknown_contact = match.group('localUnknown')

                                try:
                                    case_breakdown[date].update({
                                        'date': date,

                                        'Local - Unknown contact': unknown_contact,

                                    })
                                except KeyError:
                                    case_breakdown[date] = {
                                        'date': date,
                                        'Local - Unknown contact': unknown_contact,
                                    }
                            # under investigation
                            if re.match('.*\s(?P<underInvestigation>\d+)\sare\sUnder\sInvestigation.*',p.text):
                                match = re.match('.*\s(?P<underInvestigation>\d+)\sare\sUnder\sInvestigation.*',p.text)
                                under_investigation = match.group('underInvestigation')
                                try:
                                    case_breakdown[date].update({
                                        'date': date,
                                        'Under investigation': under_investigation
                                    })
                                except KeyError:
                                    case_breakdown[date] = {
                                        'date': date,
                                        'Under investigation': under_investigation
                                    }




                            # mean age of active cases


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
        df.set_index('date')
        df = calculateRollingAverage(window_size=7,df=df,col_to_roll='Positive Cases')
        df = calculateCasesPer100k(df, population)
        csv = path.join(getcwd(),'csv','positive_cases.csv')
        df.to_csv(csv, index=False)
        print(df.iloc[[-1]])
        
    if len(positivity_rate)>6:
        df = pd.DataFrame(positivity_rate)
        df.set_index('date')
        df = calculateRollingAverage(window_size=14,df=df,col_to_roll='Positivity Rate')
        csv = path.join(getcwd(),'csv','positivity_rate.csv')
        df.to_csv(csv, index=False)
        print(df.iloc[[-1]])

    if len(active_cases)>6:
        df = pd.DataFrame(active_cases)
        df.set_index('date')
        df = calculateRollingAverage(window_size=7,df=df,col_to_roll='Active Cases')
        csv = path.join(getcwd(),'csv','active_cases.csv')
        df.to_csv(csv, index=False)
        print(df.iloc[[-1]])

    if len(case_breakdown)>6:
        df = pd.DataFrame(list(case_breakdown.values()))
        df.set_index('date')
        csv = path.join(getcwd(),'csv','case_breakdown.csv')
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
    htmlToCsv()
    if not getenv('DEVMODE'): # only commit stuff when we're running "for realz"
        commitAndPush()
except Exception as e:
    print("Error occurred. Error was {}".format(e))