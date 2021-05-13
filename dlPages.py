from os import listdir, getcwd, path, mkdir
import requests
import datetime
import re
import git

source = path.join(getcwd(), 'src')
if not path.exists(source):
    mkdir(source)

def downloadFiles():
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
    if len(repo.untracked_files):
        print(repo.untracked_files)

try:
    # downloadFiles()
    commitAndPush()
except Exception as e:
    print("Error occurred downloading files. Error was {}".format(e))
