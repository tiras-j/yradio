# all the imports
import os
import sqlite3
import requests

import re

from create_playlist import get_song_tags, import_playlist
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

# create our little application :)
app = Flask(__name__, instance_path='/Users/fzz/yradio')

app.config.from_object(__name__)


# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'yradio.db'),
    SECRET_KEY='development key',
    USERNAME='root',
    PASSWORD='default'
))
app.config.from_envvar('YRADIO_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

# this is to run the app
# export FLASK_APP=yradio/yradio.py
# export FLASK_DEBUG=1
# flask run

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

# get the db going
# sqlite3 /tmp/yradio.db < schema.sql


def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print 'Initialized the database.'

# do the deed:
# flask initdb

# LOGIN CRAP



# SERVLET SHIT
# GET
@app.route('/')
def show_entries():
    db = get_db()

    # GET data
    # CHANGE the db select statements

    cur = db.execute('select * from Users order by USER_ID desc')
    entries = cur.fetchall()
    return render_template('index.html', entries=entries)

def add_user(user_name, password='haha', comment='super awesome'):
    db = get_db()
    # CHANGE INSERT STATEMENT
    db.execute(
        'insert into Users (USER_NAME, PASSWORD, COMMENT) values (?, ?, ?)',
        [user_name, password, comment]
    )
    db.commit()

# POST
def add_playlist(playlist_name, user_id, link, tags=[], comment='',):

    db = get_db()
    # CHANGE INSERT STATEMENT
    new_playlist_id = db.execute(
        'insert into Playlists (PLAYLIST_NAME, USER_ID, Tags, COMMENT, LINK) values (?, ?, ?, ?, ?)',
        [playlist_name, user_id, ','.join(tags), comment, link]
    )
    new_playlist_id = new_playlist_id.lastrowid
    import pdb; pdb.set_trace()
    for tag in tags:
        cur = db.execute(
            'select PLAYLISTS_LIST from Tags Where TAG_NAME={0}'.format(tag)
        ) 
        updated_lists = cur.fetchall().append(new_playlist_id)
        db.execute(
            'insert into Tags (TAG_NAME, PLAYLISTS_LIST) values (?, ?)',
            [tag, updated_lists]
        )

    db.commit()
    # flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        add_user(request.form['username'])
        return redirect(url_for('show_entries'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


@app.route('/create', methods=['POST'])
def create():

    #replace with yradio user id
    yradio_uid = 1241941697

    link = request.form['link']
    user = request.form['user']
    tags = request.form['tags'].split()
    tags.append('#{0}'.format(user))
    #add more crap
    #remove dupes

    info = re.split(':|/', link)
    playlist_id = link[-1]
    user_id = link[-3]

    # response = requests.get(
    #     "https://api.spotify.com/v1/users/{0}/playlists/{1}".format(user_id, playlist_id),
    #     headers = {'Authorization': 'Bearer {0}'.format(auth_token)}
    # )
    # #TODO handle failure
    # playlist = response.json()
    # tags = tags + get_song_tags(auth_token, playlist)

    # imported_pl = import_playlist(auth_token, yradio_uid, user_id, playlist)
    # tags = list(set(tags))
    
    add_playlist('name-ph', user, link, tags)
