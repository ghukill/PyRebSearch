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


@app.route('/fullIndexZotero')
def fullIndexZotero():
	'''
	1) Retrieve items with zot.items(), limit = something, then using start as a cursor
	* if limit 10, then bump start by 10 - KISS, keep it simple stupid.
	'''

	# settings    
	start = 0
	limit = 50
	tcount = zot.num_items()

	print "About to retrieve {tcount} items...".format(tcount=tcount)

	# iterate through all Zotero citations
	while start < tcount:	
		print "Starting at item {start}".format(start=str(start))
		zot_citation_chunk = zot.items(limit=limit,start=start,order="dateAdded")		
		
		# for each citation in chunk, do something
		# MOVE TO CELERY TASK
		for zot_citation in zot_citation_chunk:
			try:
				createFedZotObject(zot_citation)
			except:
				print "Could not create object."

		# bump cursor pointer (start) by limit per result
		start += limit

	print "finis!"
	return "All done."

# function to create / update Fed object from Zot citation
def createFedZotObject(zot_citation):
	
	'''
	RebSearch:collection-* --> Collection at RebSearch level
	RebSearch:CM-* --> Content Models at the RebSearch level
	RebSearch:ZotCM-* --> Content Models at the Zotero level

	Improvements
	1) Derive simple DC from Zotero citation? Or do this later?
	'''	
	
	# stick results in fedora object    
	PID = "RebSearch:zotero-{group_id}-{zot_key}".format(group_id=zot_citation['group_id'],zot_key=zot_citation['key'])	

	# create object
	obj_create = eulfedora.models.DigitalObject(fedora_handle, pid=PID, create=True)
	obj_create.label = zot_citation['title'].encode('utf-8').strip()	
	obj_create.save()

	# get handle
	obj_handle = fedora_handle.get_object(PID)
	
	# set preliminary relationships	
	obj_handle.add_relationship('info:fedora/fedora-system:def/relations-external#isMemberOfCollection','info:fedora/RebSearch:collection-ZoteroCitation')
	obj_handle.add_relationship('info:fedora/fedora-system:def/relations-external#hasContentModel','info:fedora/RebSearch:CM-ZoteroCitation')
	try:
		obj_handle.add_relationship('info:fedora/fedora-system:def/relations-external#hasContentModel','info:fedora/RebSearch:ZotCM-{zot_type}'.format(zot_type=zot_citation['itemType']))
	except:
		"Citation type not found."
	
	# initialized DS object
	newDS = eulfedora.models.DatastreamObject(obj_handle, "ZOTJSON", "Zotero JSON", control_group="M")    

	# construct DS object	
	newDS.mimetype = "application/json"
	newDS.content = json.dumps(zot_citation)

	print "Object {PID} created.".format(PID=PID)

	# save constructed object
	newDS.save()
	
# function to create / update Fed object from Zot citation
def updateFedZotObject(zot_citation):
	'''
	Consider making a function to update the JSON found in Fedora objects if the Zotero object changes.
	'''
	pass


# Dropbox
##############################################################################################################################
@app.route('/dropboxTesting')
def dropboxTesting():

	dropboxHandle = dropboxHandles.instantiate(session['access_token'])
	articles = dropboxHandle.metadata('/articles')
	articles_count = len(articles['contents'])      

	return render_template('dropboxTesting.html',articles_count=articles_count)



# Solr
##############################################################################################################################
'''
1) First task, index Zotero Citations 
2) Iterate through Dropbox items once files have been renamed, had full-text to Zotero Citation document
{
DOI: "10.1300/J121v17n01_14",
itemType: "journalArticle",
extra: "",
seriesText: "",
series: "",
abstractNote: "Abstract After a brief overview of the digitization activities at Florida Atlantic University Libraries, this article describes one project in detail, concentrating on various types of cooperation it reflects.",
archive: "",
title: "Cooperative Dimensions of a Digitization Project",
ISSN: "0737-7797",
archiveLocation: "",
etag: "1b429c680e173251b76df09bfa2c64ef",
journalAbbreviation: "",
issue: "1-2",
seriesTitle: "",
updated: "Fri, 26 Apr 2013 18:46:03 UTC",
tags: [ ],
accessDate: "2013-04-26 18:46:03",
libraryCatalog: "Taylor and Francis+NEJM",
volume: "17",
callNumber: "",
key: "IS3EXV83",
date: "2004",
pages: "175-185",
group_id: "341312",
shortTitle: "",
language: "",
rights: "",
url: "http://www.tandfonline.com/doi/abs/10.1300/J121v17n01_14",
publicationTitle: "Resource Sharing & Information Networks",
creators: [
{
lastName: "Adaryukov",
creatorType: "author",
firstName: "Andrew"
}
]
}
'''

@app.route('/fullSolrIndex')
def fullSolrIndex():
	pass
	# get all Zotero citation objects with Risearch	
	# Eulfedora get_subjects approach, could just as easily use sparql_query
	zot_citations = fedora_handle.risearch.get_subjects("fedora-rels-ext:isMemberOfCollection","fedora:RebSearch:collection-ZoteroCitation")	

	# for each, get ZOTJSON datastream, index in Solr /RebSearch core
	count = 0
	for zot_citation in zot_citations:
		print "Indexing {zot_citation}".format(zot_citation=zot_citation)		
		obj_handle = fedora_handle.get_object(zot_citation)
		zot_json = obj_handle.getDatastreamObject('ZOTJSON')
		zot_dict = json.loads(zot_json.content)		

		# pop lists		
		if "creators" in zot_dict:			
			creators_popped = zot_dict.pop('creators')
		if "tags" in zot_dict:			
			tags_popped = zot_dict.pop('tags')		
		

		# catch stragglers and convert integers
		for key in zot_dict:
			if type(zot_dict[key]) == "string":
				zot_dict.pop(key)
			# if type(zot_dict[key]) == "int":
			# 	zot_dict[key] = str(zot_dict[key])
		

		# prefix with "zot_" and encode in utf-8
		try:			
			prefixed_zot_citation = {"zot_"+str(key):zot_dict[key].encode('utf-8').strip() for key in zot_dict}
		except:
			fhand = open("errors.txt","a")
			fhand.write("Could not encode this one: {key}".format(key=zot_dict[key]))
			fhand.close()

		# re-add lists
		# creators
		if "creators_popped" in locals() and creators_popped != []:
			# creator_count = 1
			# creator_list = []
			# for creator in creators_popped:
			# 	try:
			# 		creator_list.append("({lastName},{firstName},{creatorType},{order})".format(lastName=creator['lastName'],firstName=creator['firstName'],creatorType=creator['creatorType'],order=str(creator_count)))					
			# 	except:
			# 		print "Could not add author"
			# prefixed_zot_citation['zot_creators'] = creator_list			
			prefixed_zot_citation['zot_creators'] = json.dumps(creators_popped)
		
		#tags		
		if "tags_popped" in locals() and tags_popped != []:
			# tag_list = []
			# for tag in tags_popped:
			# 	try:
			# 		tag_list.append("({tag},{type})".format(tag=tag['tag'],type=tag['type']))					
			# 	except:
			# 		print "Could not add tag"
			# prefixed_zot_citation['zot_tags'] = tag_list					
			prefixed_zot_citation['zot_tags'] = json.dumps(tags_popped)
		
		# set solr ID		
		prefixed_zot_citation['id'] = prefixed_zot_citation['zot_key']		

	# 	# index in Solr		
		print solr_handle.update([prefixed_zot_citation], 'json', commit=False).raw_content

		# hard break
		# count += 1
		# if count == 10:
		# 	break

	# # Finally, commit changes
	print solr_handle.commit()

	return "finished with Solr indexing"



######################################################
# Catch all - DON'T REMOVE
######################################################
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):    
	return render_template("404.html")













