import os
import time

from src.app import app
from src.periodic_runner.check_time import check_time
import settings


# periodic_runner.check_values()
check_time()

debug = True if os.getenv('ENVIRONMENT') == 'dev' else False

if not debug:
	os.environ['TZ'] = 'Europe/Berlin'
	time.tzset()

app.run(host='0.0.0.0', debug=debug)