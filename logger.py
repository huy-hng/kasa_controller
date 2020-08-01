import logging
import datetime
import os

print(os.getcwd())
if os.path.isdir('./logs'):
  os.mkdir('./logs')

log = logging.getLogger('root')
log.setLevel(logging.DEBUG)

file_formatter = logging.Formatter(
  '%(levelname)7s|%(asctime)s|%(funcName)20s()|line %(lineno)3s|%(message)3s',
  datefmt='%Y-%m-%d %H:%M:%S'
)

handler = logging.FileHandler(
            'logs/verbose-' 
            + datetime.datetime.now().strftime("%Y-%m-%d") 
            + '.log')
handler.setLevel(logging.DEBUG)
handler.setFormatter(file_formatter)
log.addHandler(handler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(file_formatter)
consoleHandler.setLevel(logging.INFO)
log.addHandler(consoleHandler)

def debug():
  log.debug('tst')
def info():
  log.info('tst')
def warn():
  log.warning('tst')
def error():
  log.error('tst')

# debug()
# info()
# warn()
# error()