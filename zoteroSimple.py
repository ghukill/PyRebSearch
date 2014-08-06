# utility for Zotero
from RebSearch.sensitive import *
from pyzotero import zotero

# instantiate
zot = zotero.Zotero(ZOTERO_USER_ID, "user", ZOTERO_API_KEY)

# most recent book
goober = zot.items(limit=1,order="dateModified")
