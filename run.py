import os
import time

from flask import cli
cli.load_dotenv()

from src.app import app
from src.periodic_runner.check_time import check_time

# periodic_runner.check_values()
check_time()

debug = True if os.getenv('ENVIRONMENT') == 'dev' else False

if not debug:
	os.environ['TZ'] = 'Europe/Berlin'
	time.tzset()

app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=debug)
