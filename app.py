from calendar import month
from numpy import byte
import requests
from requests_file import FileAdapter
from bs4 import BeautifulSoup
import re
import datetime
import pandas as pd
from os import listdir, getcwd, path, mkdir, name, getenv
import git
import subprocess

# total deaths 
#     with 3m trend
# total cases
#     with 3month trend
# people in hospital
#     with 3 month trend
# vaccines given!!
#     with 3 month trend

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
        continue

    pd.DataFrame(known_missing).to_csv(known_missing_csv,index=None)

def commitAndPush():
    count = 0
    repo = git.Repo(getcwd())
    for item in repo.index.diff(None):
        if 'csv' in item.a_path or 'index.html' in item.a_path:
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

def previous_week_range(date, weeks):
    start_date = date + datetime.timedelta(-date.weekday(), weeks=-weeks)
    end_date = date + datetime.timedelta(-date.weekday() - weeks)
    return start_date, end_date


def htmlToCsv():
    # only working on 2021 data
    date = datetime.date(year=2021, month=1, day=1)
    # create empty lists for appending the data to
    positive_cases = []
    positivity_rate = []
    active_cases = []
    dead_cases = []
    case_breakdown = {}
    c=0
    pc=0
    dc=0
    print("Converting HTML to CSV")


    while date <= datetime.date.today():

        report_date = date - datetime.timedelta(days=1)
        i = date.day
        month = date.strftime('%B').lower()
        y = date.year
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
                        words_pos = '.*\s(?P<results>\d+)\stest\sresults.*\,\sand\s(?P<positive>[none|one|two|three|four|five|six|seven|eight|nine]+).*[were|was]\spositive.*'

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

                        
                        if positive is not None:
                            if positive  > 0:
                                pos_rate = (positive / results) *100
                            else:
                                pos_rate = 0
                            positive_cases.append({
                                'date':date,
                                # 'Test results received': results,    
                                'Positive Cases': positive
                            })
                            positivity_rate.append({'date':report_date, 'Positivity Rate':pos_rate})
                            pc = pc+1
                        found = True
                        # print('The positivity rate was {}% on {} {}'.format(str(pos_rate), str(i), month))
                    
                    #deaths
                    # deaths_match = '.*\s(?P<deaths>\d+)\spersons\ssadly\ssuccumbed.*'
                    # # deaths_match = 
                    # if re.match(deaths_match, p.text):
                    #     deaths = None
                    #     if re.match(deaths_match, p.text):
                    #         match = re.match(deaths_match, p.text)
                    #         deaths = match.group('deaths')

                    #     if deaths is not None:
                    #         dead_cases.append({
                    #             'date':report_date,
                    #             'Deaths': deaths
                    #         })
                    #         dc = dc+1
                    #     found = True

                    #imported
                    if re.match('.*\s(?P<imported>\d+)\sare\sImported.*',p.text):
                        match = re.match('.*\s(?P<imported>\d+)\sare\sImported.*',p.text)
                        imported = match.group('imported')
                        try:
                            case_breakdown[report_date].update({
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
                            case_breakdown[report_date].update({
                                'date': date,
                                'Local - Known contact': known_contact,

                            })
                        except KeyError:
                            case_breakdown[report_date] = {
                                'date': report_date,
                                'Local - Known contact': known_contact,
                            }

                    # local transmission unknown contact
                    if re.match('.*\s(?P<localUnknown>\d+)\sare\sLocal\stransmission\swith\san\sunknown.*',p.text):
                        match = re.match('.*\s(?P<localUnknown>\d+)\sare\sLocal\stransmission\swith\san\sunknown.*',p.text)
                        unknown_contact = match.group('localUnknown')

                        try:
                            case_breakdown[report_date].update({
                                'date': report_date,

                                'Local - Unknown contact': unknown_contact,

                            })
                        except KeyError:
                            case_breakdown[report_date] = {
                                'date': report_date,
                                'Local - Unknown contact': unknown_contact,
                            }
                    # under investigation
                    if re.match('.*\s(?P<underInvestigation>\d+)\sare\sUnder\sInvestigation.*',p.text):
                        match = re.match('.*\s(?P<underInvestigation>\d+)\sare\sUnder\sInvestigation.*',p.text)
                        under_investigation = match.group('underInvestigation')
                        try:
                            case_breakdown[report_date].update({
                                'date': report_date,
                                'Under investigation': under_investigation
                            })
                        except KeyError:
                            case_breakdown[report_date] = {
                                'date': report_date,
                                'Under investigation': under_investigation
                            }




                    # mean age of active cases


                    #active cases
                    if re.match('.*\s(?P<active>\d+)\sactive\scases.*',p.text):
                        match = re.match('.*\s(?P<active>\d+)\sactive\scases.*',p.text)
                        active = match.group('active')
                        active_cases.append({
                            'date':report_date,
                            'Active Cases':int(active)
                            })

                        # print('There were {} active cases on {} {}'.format(str(active), str(i), month))
                        found = True

            
            if not found:
                print("Press release found for {}-{}-{} but didn't find active case numbers.".format(str(i),month,str(y)))
            date = date + datetime.timedelta(days=1)
        else:
            print('No data available for {} {}'.format(str(i), month))
            date = date + datetime.timedelta(days=1)

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

    # if len(dead_cases):
    #     df = pd.DataFrame(dead_cases)
    #     df.set_index('date')
    #     csv = path.join(getcwd(),'csv','deaths.csv')
    #     df.to_csv(csv, index=False)
    #     print(df.iloc[[-1]])


    # c is a count of the days that we did stuff for
    print(c)

    # pc is a count of the days that we got positve a counts
    # this is a proxy for how many days there was some kind of statement
    # some may contain more than one day's data
    print(pc)

def calculateDashStats():

    positive_data = pd.read_csv(path.join(source, '..','csv','positive_cases.csv'))

    # cases year to date
    df = positive_data
    total_ytd = df['Positive Cases'].sum()
    print(total_ytd)


    # positive cases in prev week
    start, end = previous_week_range(datetime.date.today(), 1)
    df = positive_data
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index(['date'])
    df = df.loc[start:end]
    one_week_ago = df['Positive Cases'].sum()
    one_week_ago_per_100k = (one_week_ago / population ) *100000
    print(one_week_ago)

    # positive cases from two weeks ago
    start, end = previous_week_range(datetime.date.today(), 2)
    df = positive_data
    df = pd.read_csv(path.join(source, '..','csv','positive_cases.csv'))
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index(['date'])
    df = df.loc[start:end]
    two_weeks_ago = df['Positive Cases'].sum()
    print(two_weeks_ago)

    # difference between prev two weeks
    diff =  one_week_ago - two_weeks_ago
    print(diff)


    # 3 month trends
    # new cases
    m3start = datetime.date.today() - datetime.timedelta(days=90)
    df = positive_data
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index(['date'])
    df = df.loc[m3start:datetime.date.today()]
    csv = path.join(getcwd(),'csv','positive_3months.csv')
    df.to_csv(csv, index=False)

    # total cases
    df = pd.read_csv(path.join(source, '..','csv','active_cases.csv'))
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index(['date'])
    df = df.loc[m3start:datetime.date.today()]
    csv = path.join(getcwd(),'csv','active_3months.csv')
    df.to_csv(csv, index=False)

    start, end = previous_week_range(datetime.date.today(), 1)
    return one_week_ago_per_100k, total_ytd, one_week_ago, diff, start, end

def updateHTML(one_week_ago_per_100k, total_ytd, one_week_ago, diff, week_start, week_end):

    week_start = week_start.strftime('%d-%b-%y')
    week_end = week_end.strftime('%d-%b-%y')

    fileout = path.join('docs','index.html')
    args = ['pandoc', 'WEBPAGE.md', '-o', fileout]
    subprocess.check_call(args)

    with open(fileout, 'r', encoding='utf-8') as file:
        content = file.readlines()

    with open(fileout, 'w', encoding='utf-8') as file:
        for line in content:

            if 'LAST_WEEK_CASES_PER_100K' in line:
                line = line.replace('LAST_WEEK_CASES_PER_100K', str(int(round(one_week_ago_per_100k,0))))
            
            if 'WEEK_FROM' in line:
                line = line.replace('WEEK_FROM', week_start)

            if 'WEEK_TO' in line:
                line = line.replace('WEEK_TO', week_end)

            if 'LAST_WEEK_CASES' in line:
                line = line.replace('LAST_WEEK_CASES',str(int(round(one_week_ago,0)))  )

            if 'DIFF' in line:
                line = line.replace('DIFF', str(diff))

            if 'CASES_YEAR_TO_DATE' in line:
                line = line.replace('CASES_YEAR_TO_DATE', str(total_ytd))

            if 'https://raw.githubusercontent.com/cj13579/bda-covid/main/csv/positivity_rate.csv' in line:
                if getenv('DEVMODE'):
                    line = line.replace('https://raw.githubusercontent.com/cj13579/bda-covid/main/csv/positivity_rate.csv', 'http://localhost:8000/csv/positivity_rate.csv')

            if 'https://raw.githubusercontent.com/cj13579/bda-covid/main/csv/positive_cases.csv' in line:
                if getenv('DEVMODE'):
                    line = line.replace('https://raw.githubusercontent.com/cj13579/bda-covid/main/csv/positive_cases.csv', 'http://localhost:8000/csv/positive_cases.csv')

            if 'https://raw.githubusercontent.com/cj13579/bda-covid/main/csv/active_cases.csv' in line:
                if getenv('DEVMODE'):
                    line = line.replace('https://raw.githubusercontent.com/cj13579/bda-covid/main/csv/active_cases.csv', 'http://localhost:8000/csv/active_cases.csv')

            file.write(line)


try:
    downloadFiles()
    htmlToCsv()
    one_week_ago_per_100k, total_ytd, one_week_ago, diff, week_start, week_end = calculateDashStats()
    updateHTML(one_week_ago_per_100k, total_ytd, one_week_ago, diff, week_start, week_end)
    if not getenv('DEVMODE'): # only commit stuff when we're running "for realz"
        commitAndPush()
except Exception as e:
    print("Error occurred. Error was {}".format(e))