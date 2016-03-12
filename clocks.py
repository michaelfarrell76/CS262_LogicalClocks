import os
import sys, getopt
import logging
import datetime
from random import randint
from multiprocessing import Process, Queue, current_process


ticks_max = 6

#http://stackoverflow.com/questions/17035077/python-logging-to-multiple-log-files-from-different-classes
def setup_logger(logger_name, log_file, level=logging.INFO):
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s : %(message)s')
    fileHandler = logging.FileHandler(log_file, mode='w')
    fileHandler.setFormatter(formatter)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)

    l.setLevel(level)
    l.addHandler(fileHandler)
    l.addHandler(streamHandler)    


def startup_machine(i, str_dt):
	global general_log
	current_pid = os.getpid()
	
	#Determine clock rate
	clock_rate = randint(1,ticks_max)
	assert(clock_rate >= 1 and clock_rate <= ticks_max)
	general_log.info('Starting machine on PID %d with clock rate: %d' % (current_pid, clock_rate))
	
	#Setup logger for each process
	logname = 'process%d' % i
	setup_logger(logname, './logs/process%d_pid%d_%s.log' % (i, current_pid, str_dt))
	process_log = logging.getLogger(logname)
	process_log.info('Process: %d, PID: %d' % (i, current_pid))

	#setup connections
	
	#setup queue

	#run and communicate

def main(argv):
	global general_log
	#Grab command line arguments
	n_machines = 0
	try:
		opts, args = getopt.getopt(argv,"n:",["n_mac="])
	except getopt.GetoptError:
		print('clocks.py -n <n_machines>')
		sys.exit(2)
	for opt, arg in opts:
		if opt in ("-n", "--n_mac"):
			n_machines = int(arg)

	#Setup logs
	if not os.path.exists('logs'):
		os.makedirs('logs')
	str_dt = datetime.datetime.now().strftime("%I_%M%p_%B_%d_%Y")
	setup_logger('general', './logs/General_2%s.log' % str_dt)
	general_log = logging.getLogger('general')

	#Start up machines
	children = []
	for i in range(n_machines):
		Process(target = startup_machine, args = (i,str_dt,)).start()        	



if __name__ == "__main__":
	main(sys.argv[1:])