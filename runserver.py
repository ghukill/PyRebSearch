# library
from twisted.web.wsgi import WSGIResource
from twisted.web.server import Site
from twisted.internet import reactor, defer, ssl
from twisted.internet.task import deferLater
from twisted.web.server import NOT_DONE_YET
from twisted.web import server, resource
from twisted.python import log
from stompest.async import Stomp
from stompest.async.listener import SubscriptionListener
from stompest.config import StompConfig
from stompest.protocol import StompSpec
import json
import logging 

# import fedoraManger2 (fm2) app
from RebSearch import app

sslContext = ssl.DefaultOpenSSLContextFactory(
	'inc/ssl/privkey.pem', 
	'inc/ssl/cacert.pem',
)

# twisted liseners
logging.basicConfig(level=logging.DEBUG)
resource = WSGIResource(reactor, reactor.getThreadPool(), app)
site = Site(resource)

if __name__ == '__main__':	
	# reactor.listenTCP( 5001, site )
	# print "RebSearch searches..."
	# reactor.run()

	reactor.listenSSL(
		5001, # integer port 
		site, # our site object, see the web howto
		contextFactory = sslContext,
	)
	print "RebSearch searches..."
	print '''                                                            
            -.+:///`                         `///:+.-            
          `-s:/  `./+/-                   -/+/.`  /:s-`          
        `++/s+:      `:+/`             `/+:`      :+s/++`        
       -o++:ss.         .//.         .//.         .ss:++o-       
    .+oss:+-+h`           `::.     .-:`           `h+-+:sso+.    
    smhos.y::h              `-:` `:-`              h::y.sohms    
    hdsss`s/-h                `---`                h-/s`sssdh    
    dd+s+ oo.s                  :                  s.oo /s+dm    
   .Ny/o+`oo-+                  :                  +-oo`+o/yN.   
   :Mo+:+.+o/:                  :                  :/o+.+:+oM:   
   +m:+-/-:o+.                  :                  .+o--/-+:N+   
   sd-:-:/.+o                   :                   o+./:-::ms   
   dd:.:.+`:+                   :                   +:`+.:.:dd   
   ms:./`+../                   :                   /..+`/.:sm   
  .h/..: /-`:```                :                ```:`-/ :..+h.  
  /m/``: /`.-////-.`            :            `.-////-.`/ :``/m/  
  /N-  : ----.-:/+so+-`         :         `-+oso::-.---- -  -N/  
  +d` `:...-://::/oooyo+-`      :      `-+oyooo/:://:--..:` `d+  
  sd .:.--::--:/++/+ssydNh/`    :    `/hNdyss+/++/:--::--.:. ds  
 `hh-:://:::/+/::///:/oosdNd/`  :  `/dNdsoo/:///::/+/::://::-hh` 
 .sh++////+/://+::///::/:/+ohs- : -sho+/:/::///::///:/+////+ohs. 
  -:+yhyssoo+:::/:-:/-.-:..-.:o/:/o:.-..:-.-/:-:/:::+oossyhyo:-  
       .-:/syhyso+/-.-.```   `./y/.`   ```.-.-/+osyhys/:-.       
              .-:+syyo+/:.``-smMMMms-``.:/+oyys+:-.              
                     .--+syyysososssyyys+:-.                     
                           ``       ``                             
	'''
	reactor.run()
