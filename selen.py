from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import os
import glob
import time

startdate = "2022-01-24"
enddate = "2022-05-19"
directory = "episoderanges/"+startdate+"to"+enddate
chrome_path = r"/Users/harryminsky/Downloads/chromedriver"
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


os.mkdir(directory)

driver = initDriver(directory)
driver.get("https://www.wnyu.org/admin")
login(driver)
# driver.get("https://www.wnyu.org/admin/episodes?order=start_at_desc&scope=with_playlists&utf8=%E2%9C%93")
# datepick(startdate,enddate)
#get to playlist page
episodes_csv = "https://www.wnyu.org/admin/episodes.csv?order=start_at_desc&q%5Bstart_at_gteq_datetime%5D="+startdate+"&q%5Bstart_at_lteq_datetime%5D="+enddate+"&scope=with_playlists&utf8=%E2%9C%93"

#getthecsvfileforids
driver.get(episodes_csv)
time.sleep(3)
filename = glob.glob(directory+"/*.csv")
#get the list of ids
df = pd.read_csv(filename[0])
df = df.drop(columns=['Description','Start at', 'End at','File url','Created at','Updated at','Image','Old','Comment','Slug','Locked'])
idnamedate = df.values.tolist()

titles = []
artists = []
showname = []
date = []
for i in idnamedate:
  driver.get(f"https://www.wnyu.org/admin/episodes/{i[0]}/tracks")
  rawtitles = [el.text for el in driver.find_elements(By.CLASS_NAME, 'col-title')]
  del rawtitles[0]
  titles.extend(rawtitles)
  rawartists = [el.text for el in driver.find_elements(By.CLASS_NAME, 'col-artist_name')]
  del rawartists[0]
  artists.extend(rawartists)
  showname.extend([i[1] for x in range(len(rawartists))])
  date.extend([i[2] for x in range(len(rawartists))])



df2 = pd.DataFrame(list(zip(titles, artists,showname,date)))
df2.to_csv(f"{startdate}_to_{enddate}.csv",encoding='utf-8',header=['title','artist','showname','date'])




