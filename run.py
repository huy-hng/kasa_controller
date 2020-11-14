import os
import time

from src.app import app
from src import periodic_runner

os.environ['TZ'] = 'Europe/Berlin'
time.tzset()

# periodic_runner.check_values()
periodic_runner.check_time()

app.run(host='0.0.0.0')