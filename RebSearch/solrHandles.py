from mysolr import Solr
import requests

# set connection through requests
session = requests.Session()
solr_handle = Solr('http://localhost:8080/solr/RebSearch', make_request=session)

