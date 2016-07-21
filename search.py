# all the imports
import os
import sqlite3
# import mysql
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)


# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'yradio.db'),
    SECRET_KEY='development key',
    USERNAME='root',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)



def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv