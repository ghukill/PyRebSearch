# RebSearch
from sensitive import *
from RebSearch.solrHandles import solr_handle

# utilities
import datetime
import hashlib



escapeRules = {'+': r'\+',
			   '-': r'\-',
			   '&': r'%26',
			   '|': r'\|',
			   '!': r'\!',
			   '(': r'\(',
			   ')': r'\)',
			   '{': r'\{',
			   '}': r'\}',
			   '[': r'\[',
			   ']': r'\]',
			   '^': r'\^',
			   '~': r'\~',			   
			   '?': r'\?',
			   ':': r'\:',			   
			   ';': r'\;',			   
			   ' ': r'+'
			   }

def escapedSeq(term):
	""" Yield the next string based on the
		next character (either this char
		or escaped version """
	for char in term:
		if char in escapeRules.keys():
			yield escapeRules[char]
		else:
			yield char

def escapeSolrArg(term):
	""" Apply escaping to the passed in query terms
		escaping special characters like : , etc"""
	term = term.replace('\\', r'\\')   # escape \ first
	return "".join([nextStr for nextStr in escapedSeq(term)])


def genUserPin(username):
	# create user pin
	date_obj = datetime.datetime.now()
	hashString = username + str(date_obj.month) + str(date_obj.day) + "WSUDOR"
	user_pin = hashlib.sha256(hashString).hexdigest()
	return user_pin	


def checkPinCreds(pin_package,check_type):
	if check_type == "purge":
		# check PINs are correct for username, and that usernames are not equal
		if pin_package['ap1'] == genUserPin(pin_package['an1']) and pin_package['ap2'] == genUserPin(pin_package['an2']) and pin_package['an1'] != pin_package['an2']:
			return True
		else:
			return False

def getLastZotSyncDate():	
		#evaluate solr response string as python dictionary
		LastZotSync = solr_handle.search(q="id:LastZotSync")
		return LastZotSync.documents[0]['last_modified'].encode('utf-8')		

def updateLastZotSyncDate():		

		#Updated LastFedoraIndex in Solr
		print "*** Updating LastFedoraIndex in Solr ***"
		update = [{'id':'LastZotSync','last_modified':'NOW'}]
		result = solr_handle.update(update,'json',commit=True)
		print result