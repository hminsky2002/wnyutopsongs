import spotipy
import pandas as pd
from spotipy.oauth2 import SpotifyOAuth

scope = "user-library-read,playlist-modify-public,playlist-modify-private"

class CreatePlaylist:
    def __init__(self,csvfile):
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
        self.song_names = self.get_song_names(csvfile)
        self.uris = self.items_list(self.song_names)

    def get_song_names(self,file):
        df = pd.read_csv(file)
        tuple_list = list(zip(df.title, df.artist))
        return tuple_list

    def geturi(self,track,artist):
        songs = self.sp.search(q="artist:" + artist + " track:" + track, type="track")['tracks']['items']
        if(len(songs) == 0):
            return
        uri = songs[0]['uri']
        return uri

    def items_list(self,tuple_list):
        urilist = []
        for i in tuple_list:
            if i is None:
                continue;
            else:
                urilist.append(self.geturi(*i))
        return list(filter(None, urilist))


# songs = get_song_names('2022-05-01_to_2022-05-03_topSongs.csv')
# uris = items_list(songs)
# playlist = sp.user_playlist_create('hdude4321','testlist3')
# sp.playlist_add_items(playlist['id'],uris)





#gets artist name
#results['albums']['items'][0]['artists'][0]['name']


# sp.album