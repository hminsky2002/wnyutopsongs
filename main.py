from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import os
import glob
import time
import re
import shutil
import pandasql as ps
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import tospotplaylist

chrome_path = r"./chromedriver"


datepattern = re.compile(r'^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$')

#fix to get around connection not secure page
def initDriver(DownloadPath):
    prefs = {"download.default_directory" : "/Users/harryminsky/PycharmProjects/wnyutopsongs/"+DownloadPath}
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-ssl-errors=yes')
    options.add_argument('--ignore-certificate-errors')
    options.add_experimental_option("prefs",prefs)
    driver = webdriver.Chrome(chrome_path,options=options)
    return driver
def login(driver):
    '''logs in to the wnyu webpage, uses tech admin creds'''
    driver.find_element(By.ID, "user_email").send_keys("tech@wnyu.org")
    driver.find_element(By.ID, "user_password").send_keys("Radioradioradio89.1")
    driver.find_element(By.NAME, "commit").click()
def datepick(start,end):
    '''takes a start and end date range as strings in the form YYYY-MM-DD'''
    driver.find_element(By.NAME, "q[start_at_gteq_datetime]").send_keys(start)
    driver.find_element(By.NAME, "q[start_at_lteq_datetime]").send_keys(end)
    driver.find_element(By.NAME, "commit").click()
def popExtend(pop,listy):
    del pop[0]
    listy.extend(pop)
# def populatelist(listy,colname):
#     '''populates a list with the relevant elements, returns number of items added'''
#     rawlist = [el.text for el in driver.find_elements(By.CLASS_NAME, colname)]
#     del rawlist[0]
#     listy.extend(rawlist)
#     return len(rawlist)

print("tool to get chart data from wnyu.org admin site")

# startdate = "2022-05-05"
# enddate = "2022-05-06"
startdate = input("enter a start date of form YYYY-MM-DD: ")
while not re.match(datepattern,startdate):
    startdate = input("please enter a valid start date of form YYYY-MM-DD: ")

enddate = input("enter an end date of form YYYY-MM-DD: ")
while not re.match(datepattern,enddate):
    end = input("please enter a valid end date of form YYYY-MM-DD: ")
songlimit = input('enter a song limit')
albumlimit = input('enter an album limit')
artistlimit = input('enter an artist limit')

directory = startdate+"to"+enddate

#create new directory for ids csv file
os.mkdir(directory)


#intitalize driver with proper download folder
driver = initDriver(directory)

#get to homepage and login, if different creds are required change vars in login method
driver.get("https://www.wnyu.org/admin")
login(driver)

#get to playlist page
episodes_csv = "https://www.wnyu.org/admin/episodes.csv?order=start_at_desc&q%5Bstart_at_gteq_datetime%5D="+startdate+"&q%5Bstart_at_lteq_datetime%5D="+enddate+"&scope=with_playlists&utf8=%E2%9C%93"

#get the csv file for ids
driver.get(episodes_csv)
time.sleep(3)
filename = glob.glob(directory+"/*.csv")
#get the list of ids
df = pd.read_csv(filename[0])
df = df.drop(columns=['Description','Start at', 'End at','File url','Created at','Updated at','Image','Old','Comment','Slug','Locked'])
idNameDate = df.values.tolist()

titles = []
artists = []
albums = []
showName = []
date = []
for i in idNameDate:
    driver.get(f"https://www.wnyu.org/admin/episodes/{i[0]}/tracks")
    rawtitles = []
    rawartists = []
    rawalbums = []
    for parent in driver.find_elements(By.TAG_NAME,"tr"):
        rawtitles.append(parent.find_element(By.CLASS_NAME,"col-title").text)
        rawartists.append(parent.find_element(By.CLASS_NAME, "col-artist_name").text)
        rawalbums.append(parent.find_element(By.CLASS_NAME, "col-release_name").text)
    popExtend(rawtitles,titles)
    popExtend(rawartists,artists)
    popExtend(rawalbums,albums)
    showName.extend([i[1] for x in range(len(rawtitles))])
    date.extend([i[2] for x in range(len(rawtitles))])


fullsheet = pd.DataFrame(list(zip(titles, artists, albums, showName, date)))


os.mkdir(f"output/{startdate}_to_{enddate}")

fullsheet.to_csv(f"output/{startdate}_to_{enddate}/{startdate}_to_{enddate}_all.csv",header=['title', 'artist', 'albums', 'showname', 'date'])

#quick rework to allow for subquery
fullsheet = pd.read_csv(f'output/{startdate}_to_{enddate}/{startdate}_to_{enddate}_all.csv')
artistsdf = fullsheet[['artist','showname','date']]
artistsdf = artistsdf.drop_duplicates()


topartists = ps.sqldf('''Select artist, count(*) as n
                          FROM artistsdf
                          where artist != ""
                          group by artist
                          having count(*) > 1
                          order by count(*) DESC
                          limit '''+artistlimit)
topartists.to_csv(f"output/{startdate}_to_{enddate}/{startdate}_to_{enddate}_topArtists.csv",header=['artist', 'plays'])

topsongs = ps.sqldf('''SELECT title, artist, count(*)
                        FROM fullsheet
                        where showname != "Songland NYU" and title != "" and artist != ""
                        group by title, artist
                        order by count(*) DESC
                        limit '''+songlimit)
topsongs.to_csv(f"output/{startdate}_to_{enddate}/{startdate}_to_{enddate}_topSongs.csv",header=['title','artist', 'plays'])

topalbums = ps.sqldf('''SELECT albums, artist, COUNT(*) as plays
                        FROM fullsheet
                        WHERE albums != ""
                        GROUP BY albums,artist
                        HAVING plays > 1
                        ORDER BY plays DESC
                        limit '''+albumlimit)
topalbums.to_csv(f"output/{startdate}_to_{enddate}/{startdate}_to_{enddate}_topAlbums.csv",header=['album','artist', 'plays'])

driver.close()

#create a playlist object to output the songs to a playlist
playlistobject = tospotplaylist.CreatePlaylist(f'output/{startdate}_to_{enddate}/{startdate}_to_{enddate}_topSongs.csv')

#for storing playlist id
templist = playlistobject.sp.user_playlist_create('hdude4321',f'WNYU top songs {startdate} to {enddate}')

#for adding songs
playlistobject.sp.playlist_add_items(templist['id'],playlistobject.uris)



#upload the files to gdrive
gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)
uploadables = glob.glob(f'output/{startdate}_to_{enddate}/'+"/*.csv")
for f in uploadables:
    file = drive.CreateFile({'parents': [{'id':'1GPgIjuTSoFwtkcXzFK69TqgNRdmdzYzM'}]})
    file.SetContentFile(f)
    file.Upload()
shutil.rmtree(directory)



