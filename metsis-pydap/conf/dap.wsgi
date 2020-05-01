import site
from pydap.wsgi.app import DapServer
application = DapServer('/var/www/localhost/pydap/data')


