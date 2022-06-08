from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
startdate = "2022-05-29"
enddate = "2022-06-11"
chrome_path = r"/Users/harryminsky/Downloads/chromedriver"

def login():
    '''logs in to the wnyu webpage, uses tech admin creds'''
    driver.find_element(By.ID, "user_email").send_keys("tech@wnyu.org")
    driver.find_element(By.ID, "user_password").send_keys("Radioradioradio89.1")
    driver.find_element(By.NAME, "commit").click()

def datepick(start,end):
    '''takes a start and end date range as strings in the form YYYY-MM-DD'''
    driver.find_element(By.NAME, "q[start_at_gteq_datetime]").send_keys(start)
    driver.find_element(By.NAME, "q[start_at_lteq_datetime]").send_keys(end)
    driver.find_element(By.NAME, "commit").click()




#fix to get around connection not secure page
options = webdriver.ChromeOptions()
options.add_argument('--ignore-ssl-errors=yes')
options.add_argument('--ignore-certificate-errors')
driver = webdriver.Chrome(chrome_path,options=options)

driver.get("https://www.wnyu.org/admin")
login()
#get to playlist page
driver.get("https://www.wnyu.org/admin/episodes?scope=with_playlists")

datepick(startdate,enddate)
#get the list of episodes in the range this won't work for larger ranges right now
text_contents = [el.text.split(' ') for el in driver.find_elements(By.TAG_NAME, 'tr')]

#construct id list
ids = []
for i in range(1,len(text_contents)):
    ids.append(text_contents[i][0])

titles = []
names = []
for i in ids:
  driver.get(f"https://www.wnyu.org/admin/episodes/{int(i)}/tracks")
  rawtitles = [el.text for el in driver.find_elements(By.CLASS_NAME, 'col-title')]
  del rawtitles[0]
  titles.extend(rawtitles)
  rawnames = [el.text for el in driver.find_elements(By.CLASS_NAME, 'col-artist_name')]
  del rawnames[0]
  names.extend(rawnames)


df = pd.DataFrame(list(zip(titles, names)))
df.to_csv(f"{startdate}_to_{enddate}.csv",encoding='utf-8',header=['title','artist'])





