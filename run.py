import os
import time

from src.app import app
from src.periodic_runner import tl

os.environ['TZ'] = 'Europe/Berlin'
time.tzset()

tl.start()
app.run(debug=True, host='0.0.0.0')