import time
import requests

# endpoint = 'https://130.83.4.219:5443'
endpoint = 'http://localhost:5000'


requests.get(endpoint+'/tom/brightness?target=1')
time.sleep(1)
requests.get(endpoint+'/nom/set_active?duration=2')