# utility for Zotero
from sensitive import *
from pyzotero import zotero

# instantiate
zot = zotero.Zotero(zotero_user_id, "user", zotero_api_key)

# most recent book
goober = zot.items(limit=1,order="dateModified")
