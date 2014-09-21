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
import re
import requests

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



# Sync
############################################################################################################
@app.route('/fullSync')
def fullSync():
	'''
	For each citation in Zotero:
		create object in Fedora
		update Zotero "extra" field with guessed filename
		check for filename in Dropbox:
			if available, add as datastraem to Fedora
		index ZOTJSON and article fulltext in Solr		
	'''

	



######################################################
# Catch all - DON'T REMOVE
######################################################
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):    
	return render_template("404.html")













