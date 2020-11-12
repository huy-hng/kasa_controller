import time
import requests

# endpoint = 'https://130.83.4.219:5443'
endpoint = 'http://localhost:5000'


# requests.get(endpoint+'/profile/wakeup')
requests.get(endpoint+'/on')
# requests.get(endpoint+'/disengage')
requests.get(endpoint+'/nvl/brightness/100')
requests.get(endpoint+'/nvl/temp/100') 