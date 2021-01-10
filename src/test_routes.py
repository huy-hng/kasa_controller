import time
import requests

# endpoint = 'https://130.83.4.219:5443'
endpoint = 'http://localhost:5000'


requests.get(endpoint+'/nom/profile/wakeup')
# requests.get(endpoint+'/nom/color_temp?target=0')
