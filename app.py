from dotenv import load_dotenv
import os
from flask import Flask, redirect, session, request, render_template, make_response
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
import sqlite3
from flask import jsonify

load_dotenv()

# this code is retarded because it's caching everyones user auth in the .cache file
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

# This is what connects the front end to the backend
app = Flask(__name__)
app.secret_key = client_secret

# DATABASE
db = SQLAlchemy()
db_name = 'tunetown.db'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    
    # Relationship with friends
    friends = db.relationship('Friendship', foreign_keys='Friendship.user_id', backref='user', lazy=True)

    # Relationship with posts
    posts = db.relationship('Post', backref='author', lazy=True)

class Friendship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db.init_app(app)

with app.app_context():
    db.create_all()

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

    # LOAD DB
    # try:
    #     users = db.session.execute(db.select(User)
    #         .order_by(User.username)).scalars()

    #     username_text = '<ul>'
    #     for user in users:
    #         username_text += '<li>' + user.username + ', ' + str(user.id) + '</li>'
    #     username_text += '</ul>'
    #     return username_text
    # except Exception as e:
    #     # e holds description of the error
    #     error_text = "<p>The error:<br>" + str(e) + "</p>"
    #     hed = '<h1>Something is broken.</h1>'
    #     return hed + error_text

    # user variables
    username = user_profile['display_name']
    pfp = user_profile['images'][0]['url'] if user_profile['images'] else ''
    id = user_profile['id']

    topSongs = sp.current_user_top_tracks(limit=6)
    names = []
    pics = []
    artists = []
    previews = []
    for song in topSongs['items']:
        names.append(song['name'])
        previews.append(song['preview_url'])
        for artist in song['artists']:
            artists.append(artist['name'])
            break # this makes sure only the first artist is appended
        album_id = song['album']['id']
        album_info = sp.album(album_id)
        cover_art_url = album_info['images'][0]['url'] if len(album_info['images']) > 0 else None
        pics.append(cover_art_url)
    songData = zip(pics, names, artists, previews)
    
    return render_template('profile.html', username=username, pfp=pfp, id=id, songData=songData)

@app.route('/callback')
def callback():
    # Parse authorization response
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['spotify_token_info'] = token_info
    return redirect('/')

@app.route('/logout')
def logout():
    session['spotify_token_info'] = None
    session.clear()
    return render_template('logout.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/create_post')
def create_post():
    return render_template('create_post.html')

@app.route('/post')
def post():
    #SQL logic goes here
    return 

# METHODS
# Route to add a new user
@app.route('/add_user', methods=['POST'])
def add_user(username):

    # # Check if username is provided
    # if not username:
    #     return jsonify({'message': 'Username is required'}), 400

    # Check if the username already exists
    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists'}), 400

    # Create a new user object
    new_user = User(username=username)

    # Add the user to the session and commit changes to the database
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User added successfully'}), 201

@app.route('/add_post', methods=['POST'])
def add_post(song_id):

    # Create a new user object
    # TODO this prob is not correct
    new_post = Post(content = song_id, user_id = User.id)

    # Add the user to the session and commit changes to the database
    db.session.add(new_post)
    db.session.commit()

    return jsonify({'message': 'User added successfully'}), 201

if __name__ == '__main__':
    app.run(port=5000, debug=True)
