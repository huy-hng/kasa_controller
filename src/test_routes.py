import time
import requests

endpoint = 'http://0.0.0.0:5000/'

# requests.get(endpoint+'brightness/30')
# time.sleep(2)
# requests.get(endpoint+'brightness/1/3')
# time.sleep(2)
# requests.get(endpoint+'lamp')
# time.sleep(0.5)
requests.delete(endpoint+'lamp')
# requests.get(endpoint+'brightness/100')