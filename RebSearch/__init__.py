# root file, app instantiator

# modules / packages import
from flask import Flask, render_template, g
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, MetaData
from flask.ext.login import LoginManager
from pyzotero import zotero

# configs
from RebSearch.sensitive import *

# create app
app = Flask(__name__)

# setup db
db = SQLAlchemy(app)
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], convert_unicode=True)
metadata = MetaData(bind=engine)
db_con = engine.connect()

# fire up Zotero connection
zot = zotero.Zotero(ZOTERO_USER_ID, "user", ZOTERO_API_KEY)

# start up login
# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = 'login'

# get handlers
import views






