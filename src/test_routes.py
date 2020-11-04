import time
import requests

# endpoint = 'https://130.83.4.219:5443'
endpoint = 'http://localhost:5000'


# requests.get(endpoint+'/nvl/brightness/100')
# requests.get(endpoint+'/nvl/temp/0')
requests.get(endpoint+'/override/2')