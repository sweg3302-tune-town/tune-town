from dotenv import load_dotenv
import os
from flask import Flask, redirect, session, request, render_template
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pyodbc

load_dotenv()

# this code is retarded because it's caching everyones user auth in the .cache file
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

# This is what connects the front end to the backend
app = Flask(__name__)
app.secret_key = client_secret

# Initialize SpotifyOAuth object within the route
sp_oauth = SpotifyOAuth(
        client_id = os.getenv("CLIENT_ID"),
        client_secret = os.getenv("CLIENT_SECRET"),
        redirect_uri = 'http://localhost:5000/callback',
        scope = 'user-read-private user-top-read user-library-read',
        cache_path=None
    )

def htmlForLoginButton():
    auth_url = sp_oauth.get_authorize_url()
    htmlLoginButton = "<a href='" + auth_url + "'>Login to Spotify</a>"
    return htmlLoginButton

# --- routes ---
@app.route('/')
def index():
  
    # Get user's profile information
    token_info = session.get('spotify_token_info')

    if not token_info or sp_oauth.is_token_expired(token_info):
        # return redirect('/callback')
        return htmlForLoginButton()
    
    sp = spotipy.Spotify(auth=session['spotify_token_info']['access_token'])
    user_profile = sp.current_user()

    # user variables
    username = user_profile['display_name']
    pfp = user_profile['images'][0]['url'] if user_profile['images'] else ''
    id = user_profile['id']  

    topSongs = sp.current_user_top_tracks(limit=6)
    names = []
    pics = []
    previews = []
    for song in topSongs['items']:
        names.append(song['name'])
        previews.append(song['preview_url'])
        album_id = song['album']['id']
        album_info = sp.album(album_id)
        cover_art_url = album_info['images'][0]['url'] if len(album_info['images']) > 0 else None
        pics.append(cover_art_url)
    songData = zip(pics, names, previews)
    
    return render_template('profile.html', username=username, pfp=pfp, id=id, songData=songData)

@app.route('/callback')
def callback():
    # Parse authorization response
    code = request.args.get('code')
    # print(str(code))
    token_info = sp_oauth.get_access_token(code)
    # print(token_info)
    session['spotify_token_info'] = token_info
    return redirect('/')

# TODO needs to be implemented
@app.route('/logout')
def logout():
    session['spotify_token_info'] = None
    session.clear()
    return render_template('logout.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.rout('/friends')
def friends():
    class User:
        def __init__(self):
            self.UserID = None
            self.SpotifyHandle = None

    class Friendship:
        def __init__(self):
            self.FriendshipID = None
            self.User1ID = None
            self.User2ID = None
            self.DateFriended = None

    class DatabaseContext:
        def __init__(self, connection_string):
            self.connection_string = connection_string
            self.users = []
            self.friendship_dict = {}

        def return_friends(self):
            with pyodbc.connect(self.connection_string) as connection:
                cursor = connection.cursor()
                query = """SELECT u.UserID, u.SpotifyHandle, f.User2ID
                        FROM Users u 
                        INNER JOIN Friendships f ON u.UserID = f.User1ID 
                        GROUP BY u.UserID, u.SpotifyHandle, f.User2ID"""
                cursor.execute(query)
                rows = cursor.fetchall()
                for row in rows:
                    u = User()
                    f = Friendship()
                    u.UserID = row.UserID
                    u.SpotifyHandle = row.SpotifyHandle
                    f.User2ID = row.User2ID
                    self.friendship_dict[u.SpotifyHandle] = f.User2ID

            return self.friendship_dict


if __name__ == '__main__':
    app.run(port=5000, debug=True)
