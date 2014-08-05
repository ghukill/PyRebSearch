# Dropbox Handles

# dropbox
import dropbox

def instantiate(access_token):
	return dropbox.client.DropboxClient(access_token)  