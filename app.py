from dotenv import load_dotenv
import os
from flask import Flask, redirect, session, request, render_template
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import logging

load_dotenv()

## this code is retarded because it's caching everyones user auth in the .cache file
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

# This is what connects the front end to the backend
app = Flask(__name__)
app.secret_key = client_secret

# logger = logging.getLogger(__name__)

# class CacheHandler():
#     """
#     An abstraction layer for handling the caching and retrieval of
#     authorization tokens.

#     Custom extensions of this class must implement get_cached_token
#     and save_token_to_cache methods with the same input and output
#     structure as the CacheHandler class.
#     """

#     def get_cached_token(self):
#         """
#         Get and return a token_info dictionary object.
#         """
#         # return token_info
#         raise NotImplementedError()

#     def save_token_to_cache(self, token_info):
#         """
#         Save a token_info dictionary object to the cache and return None.
#         """
#         raise NotImplementedError()
#         return None

# class DummyCacheHandler(CacheHandler):
#     """
#     A dummy cache handler that does not store anything.
#     """

#     def get_cached_token(self):
#         logger.debug("Token retrieval from dummy cache.")
#         return None

#     def save_token_to_cache(self, token_info):
#         logger.debug("Token not saved to dummy cache.")

# Initialize SpotifyOAuth object within the route
sp_oauth = SpotifyOAuth(
        client_id = os.getenv("CLIENT_ID"),
        client_secret = os.getenv("CLIENT_SECRET"),
        redirect_uri = 'http://localhost:5000/callback',
        scope = 'user-library-read',
        cache_handler=DummyCacheHandler()
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
    print(str(code))
    token_info = sp_oauth.get_access_token(code)
    print(token_info)
    session['spotify_token_info'] = token_info
    return redirect('/')

@app.route('/logout')
def logout():
    session['spotify_token_info'] = None
    return redirect('/')

if __name__ == '__main__':
    app.run(port=5000, debug=True)

