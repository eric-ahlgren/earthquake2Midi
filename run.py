#!/usr/bin/env python
from app import app
import ssl

context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
context.load_cert_chain('/Users/ericahlgren/.localhost-ssl/cert.pem','/Users/ericahlgren/.localhost-ssl/key.pem')
app.run(debug=True, ssl_context=context)