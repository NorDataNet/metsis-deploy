import site
from pydap.wsgi.app import DapServer
application = DapServer('/var/www/sites/pydap/server/data')


