from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)
file1 = drive.CreateFile({'parents': [{'id':'1GPgIjuTSoFwtkcXzFK69TqgNRdmdzYzM'}]})
file1.SetContentFile('output/2022-06-13_to_2022-06-20/2022-06-13_to_2022-06-20_all.csv')
file1.Upload()
