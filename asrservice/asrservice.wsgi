from asrservice import asrservice
import clam.clamservice
application = clam.clamservice.run_wsgi(asrservice)