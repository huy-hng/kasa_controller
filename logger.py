import logging
import datetime
import os

if not os.path.isdir('./logs'):
	os.mkdir('./logs')

log = logging.getLogger('root')
log.setLevel(logging.DEBUG)

file_formatter = logging.Formatter(
	'%(levelname)7s|%(asctime)s|%(funcName)20s()|line %(lineno)3s|%(message)3s',
	datefmt='%Y-%m-%d %H:%M:%S'
)

def file_handler(folder, log_level):
	if not os.path.isdir(f'./logs/{folder}'):
		os.mkdir(f'./logs/{folder}')

	handler = logging.FileHandler(
							f'logs/{folder}/' 
							+ datetime.datetime.now().strftime("%Y-%m-%d") 
							+ '.log')
	handler.setLevel(log_level)
	handler.setFormatter(file_formatter)
	log.addHandler(handler)

file_handler('verbose', logging.DEBUG)
file_handler('info', logging.INFO)

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

if __name__ == '__main__':
	debug()
	info()
	warn()
	error()
	