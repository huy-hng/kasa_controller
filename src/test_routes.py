import time
import requests

endpoint = 'http://0.0.0.0:5000'

requests.get(endpoint+'/nvl/temp/100')



# requests.get(endpoint+'/temp/0')
requests.get(endpoint+'/brightness/1/5')
time.sleep(1)
requests.get(endpoint+'/brightness/100/5')
# requests.delete(endpoint+'/brightness')
# requests.get(endpoint+'/lamp/0')
# requests.delete(endpoint+'/lamp')
# requests.get(endpoint+'/brightness/100')