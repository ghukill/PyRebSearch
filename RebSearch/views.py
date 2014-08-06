# REBSEARCH
###########

# RebSearch
from RebSearch import app, models, db, zot, utilities
from RebSearch.sensitive import *

# python modules
import time
import json
import pickle
import sys
from uuid import uuid4
import json
import unicodedata
import shlex, subprocess
import socket
import hashlib

# dropbox
import dropbox
import dropboxHandles
from dropbox.client import DropboxOAuth2Flow, DropboxClient

# eulfedora
import eulfedora

# flask proper
from flask import render_template, request, session, redirect, make_response, Response
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime

# login
from flask import flash, url_for, abort, g
from flask.ext.login import login_user, logout_user, current_user, login_required

# models
from models import User, ROLE_USER, ROLE_ADMIN

# forms
from flask_wtf import Form
from wtforms import TextField

# get celery instance / handle
from cl.cl import celery

# Solr
from solrHandles import solr_handle

# Fedora
from fedoraHandles import fedora_handle

# session data secret key
####################################
app.secret_key = 'RebSearch'
####################################


# Dropbox Login
############################################################################################################
@app.route('/dropboxLogin')
def dropboxLogin():
    if not 'access_token' in session:
        return redirect(url_for('dropbox_auth_start'))
    else:
        return redirect(url_for('home'))

@app.route('/dropbox-auth-start')
def dropbox_auth_start():
    return redirect(get_auth_flow().start())

@app.route('/dropbox-auth-finish')
def dropbox_auth_finish():
    try:
        access_token, user_id, url_state = get_auth_flow().finish(request.args)
    except:
        abort(400)
    else:
        session['access_token'] = access_token
    return redirect(url_for('home'))

def get_auth_flow():
    redirect_uri = url_for('dropbox_auth_finish', _external=True)
    return DropboxOAuth2Flow(DROPBOX_APP_KEY, DROPBOX_APP_SECRET, redirect_uri,
                             session, 'dropbox-auth-csrf-token')


# General
############################################################################################################

# home
@app.route('/')
def home():
    if not 'access_token' in session:
        return redirect(url_for('dropbox_auth_start'))
    
    else:
        access_token = session['access_token']
        client = dropbox.client.DropboxClient(access_token)
        account_info = client.account_info()

        print ZOTERO_USER_ID

        return render_template('index.html',account_info=account_info,ZOTERO_USER_ID=ZOTERO_USER_ID)

@app.route('/logout')
def logout():
    if not 'access_token' in session:
        return "You ain't logged in!"
    
    else:
        session.pop('access_token', None)
        print session
        return "Ya'll come back now, ya hear!"


# Zotero
##############################################################################################################################

@app.route('/zoteroTesting')
def zoteroTesting():
    goober = zot.items(limit=1,order="dateModified") 
    last_modified = utilities.getLastZotSyncDate()   

    return render_template('zoteroTesting.html',goober=goober,last_modified=last_modified)


@app.route('/syncZotero')
def syncZotero():
    '''
    1) Check last Zot-Sync date in Solr
    2) Retrieve all items from Zotero modified after that date
    3) For each
        a) get metadata in useful form
        b) create / update object in Fedora (PID = RebSearch_Account:ZoteroID)
    4) Update last Zot-Synce date in Solr
    '''

    # get last sync date
    LastZotSyncDate = utilities.getLastZotSyncDate()


    

    return render_template('syncZotero.html',goober=goober)


# Dropbox
##############################################################################################################################
@app.route('/dropboxTesting')
def dropboxTesting():

    dropboxHandle = dropboxHandles.instantiate(session['access_token'])
    articles = dropboxHandle.metadata('/articles')
    articles_count = len(articles['contents'])      

    return render_template('dropboxTesting.html',articles_count=articles_count)



######################################################
# Catch all - DON'T REMOVE
######################################################
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):    
	return render_template("404.html")













