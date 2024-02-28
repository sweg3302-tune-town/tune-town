from dotenv import load_dotenv
import os
from flask import Flask, redirect, session, request, render_template
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from CacheHandler import FlaskSessionCacheHandler

import requests

load_dotenv()

## this code is retarded because it's caching everyones user auth in the .cache file
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

# This is what connects the front end to the backend
app = Flask(__name__)
app.secret_key = client_secret

session = requests.Session()
myCacheHandler = FlaskSessionCacheHandler(session=session)

# Initialize SpotifyOAuth object within the route
sp_oauth = SpotifyOAuth(
        client_id = os.getenv("CLIENT_ID"),
        client_secret = os.getenv("CLIENT_SECRET"),
        redirect_uri = 'http://localhost:5000/callback',
        scope = 'user-read-private user-top-read user-library-read',
        # cache_path=None
        cache_handler=myCacheHandler
    )

def htmlForLoginButton():
    auth_url = getSPOauthURI()
    htmlLoginButton = "<a href='" + auth_url + "'>Login to Spotify</a>"
    return htmlLoginButton

def getSPOauthURI():
    auth_url = sp_oauth.get_authorize_url()
    return auth_url

@app.route('/')
def index():
  
    # Get user's profile information
    token_info = session.get('spotify_token_info')

    if not token_info or sp_oauth.is_token_expired(token_info):
        # return redirect('/callback')
        return htmlForLoginButton()
    
    # sp = spotipy.Spotify(auth=session['spotify_token_info']['access_token'])
    sp = spotipy.Spotify(auth_manager=sp_oauth)
    user_profile = sp.current_user()
    username = user_profile['display_name']
    # Get user's profile picture if available
    pfp = user_profile['images'][0]['url'] if user_profile['images'] else ''
    id = user_profile['id']  
    return render_template('index.html', username=username, pfp=pfp, id=id)

@app.route('/callback')
def callback():
    # Parse authorization response
    code = request.args.get('code')
    # print(str(code))
    token_info = sp_oauth.get_access_token(code)
    # print(token_info)
    session['spotify_token_info'] = token_info
    return redirect('/')

@app.route('/logout')
def logout():
    session['spotify_token_info'] = None
    return redirect('/')

if __name__ == '__main__':
    app.run(port=5000, debug=True)

