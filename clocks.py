import asyncore
import socket
import threading
from threading import Thread
import time
import sys
import random
import logging
import os
import datetime
from multiprocessing import Process, current_process, Queue

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

def dump_queue(queue):
    """
    Empties all pending items in a queue and returns them in a list.
    """
    result = []
    time.sleep(.1)
    while not queue.empty():
        result.append(queue.get())
    time.sleep(.1)
    return result

class MessageHandler(asyncore.dispatcher_with_send):
    def set_queue(self, q):
        self.q = q

    def handle_read(self):
        data = self.recv(1024)
        if data != '':
            # print('Message received ' + str(data))
            self.q.put(data)

class MessageServer(asyncore.dispatcher):

    def __init__(self, host, port, queue, lock):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)
        self.q = queue
        self.q_num_add = 0
        self.port = port
        self.lock = lock

    def handle_accept(self):
        self.lock.acquire()
        self.q_num_add = self.q_num_add + 1
        self.lock.release()
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            handler = MessageHandler(sock)
            handler.set_queue(self.q)

def start_servers(servers):
    try:
        asyncore.loop()
    except Exception, e:
        if e[0] == 9:
            print('Servers closed')
        else:
            raise e
            for server in servers:
                server.close() 
            sys.exit(0)

def send_message(message, port_num):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('127.0.0.1', port_num))
    sock.send(message)
    sock.close()

def machine_operate(server, port_nums, clock_rate, m_id, upper_random_num, tot_time=60):
    global general_log
    current_pid = os.getpid()
    start_time = time.time()
    general_log.info('Starting machine on PID %d with clock rate: %d' % (current_pid, clock_rate))
        #Setup logger for each process

    logname = 'process%d' % m_id
    setup_logger(logname, './logs/process%d_internal_event_%s.log' % (m_id, str((upper_random_num-2.0)/upper_random_num)[0:4]))
    process_log = logging.getLogger(logname)
    process_log.info('Process: %d, PID: %d' % (m_id, current_pid))

    # Get the server to start
    Thread(target=start_servers, args=([server],)).start()
    logical_clock = 0
    q_remove = 0
    q = server.q
    port_nums = port_nums[:]
    port_nums.remove(server.port)
    for t in range(tot_time):
        for j in range(clock_rate):
            sleep_start_time = time.time()
            logical_clock += 1 
            if not q.empty():
                lc_value = q.get()
                print('Machine ' + str(m_id) + ' (clock rate = ' + str(clock_rate) + ')' + ' received message with lc value of ' + lc_value + ' with queue size of ' + str(server.q_num_add - q_remove) + ' at ' +  str(time.time() - start_time)[0:5] + 's with logical clock of ' + str(logical_clock))
                process_log.info('Machine ' + str(m_id) + ' (clock rate = ' + str(clock_rate) + ')' + ' received message with lc value of ' + lc_value + ' with queue size of ' + str(server.q_num_add - q_remove) + ' at ' +  str(time.time() - start_time)[0:5] + 's with logical clock of ' + str(logical_clock))
                general_log.info('Machine ' + str(m_id) + ' (clock rate = ' + str(clock_rate) + ')' + ' received message with lc value of ' + lc_value + ' with queue size of ' + str(server.q_num_add - q_remove) + ' at ' +  str(time.time() - start_time)[0:5] + 's with logical clock of ' + str(logical_clock))
                logical_clock = max(logical_clock, int(lc_value))
                q_remove = q_remove + 1
            randint = random.randint(1, upper_random_num)
            if randint == 1:
                print('Machine ' + str(m_id) +  ' (clock rate = ' + str(clock_rate) + ')' + ' sending to Machine ' + str(port_nums[0] - 3004) + ' logical clock value of ' + str(logical_clock) + ' at ' +  str(time.time() - start_time)[0:5] + 's')
                process_log.info('Machine ' + str(m_id) +  ' (clock rate = ' + str(clock_rate) + ')' + ' sending to Machine ' + str(port_nums[0] - 3004) + ' logical clock value of ' + str(logical_clock) + ' at ' +  str(time.time() - start_time)[0:5] + 's')
                general_log.info('Machine ' + str(m_id) +  ' (clock rate = ' + str(clock_rate) + ')' + ' sending to Machine ' + str(port_nums[0] - 3004) + ' logical clock value of ' + str(logical_clock) + ' at ' +  str(time.time() - start_time)[0:5] + 's')
                send_message(str(logical_clock), port_nums[0])
            elif randint == 2:
                print('Machine ' + str(m_id) +  ' (clock rate = ' + str(clock_rate) + ')' + ' sending to Machine ' + str(port_nums[0] - 3004) + ' logical clock value of ' + str(logical_clock) + ' at ' +  str(time.time() - start_time)[0:5] + 's')
                process_log.info('Machine ' + str(m_id) +  ' (clock rate = ' + str(clock_rate) + ')' + ' sending to Machine ' + str(port_nums[0] - 3004) + ' logical clock value of ' + str(logical_clock) + ' at ' +  str(time.time() - start_time)[0:5] + 's')
                general_log.info('Machine ' + str(m_id) +  ' (clock rate = ' + str(clock_rate) + ')' + ' sending to Machine ' + str(port_nums[0] - 3004) + ' logical clock value of ' + str(logical_clock) + ' at ' +  str(time.time() - start_time)[0:5] + 's')
                send_message(str(logical_clock), port_nums[1])
            else:
                print('Machine ' + str(m_id) +  ' (clock rate = ' + str(clock_rate) + ')' + ' has internal event at ' +  str(time.time() - start_time)[0:5] + 's with logical clock value of ' + str(logical_clock))
                process_log.info('Machine ' + str(m_id) +  ' (clock rate = ' + str(clock_rate) + ')' + ' has internal event at ' +  str(time.time() - start_time)[0:5] + 's with logical clock value of ' + str(logical_clock))
                general_log.info('Machine ' + str(m_id) +  ' (clock rate = ' + str(clock_rate) + ')' + ' has internal event at ' +  str(time.time() - start_time)[0:5] + 's with logical clock value of ' + str(logical_clock))

            time.sleep(1.0/clock_rate - (time.time() - sleep_start_time))
    # print 'Machine' + str(clock_rate) + str(dump_queue(q))

if __name__ == '__main__':
    try:
        # Upper random number
        upper_random_num = 10

        #Setup logs
        if not os.path.exists('logs'):
            os.makedirs('logs')
        str_dt = datetime.datetime.now().strftime("%I_%M%p_%B_%d_%Y")
        setup_logger('general', './logs/General_internal_event_%s.log' % (str((upper_random_num-2.0)/upper_random_num)[0:3]))

        general_log = logging.getLogger('general')

        # Initialize all the servers
        start_port = 3005
        port_nums = [start_port, start_port+1, start_port+2]

        server1 = MessageServer('localhost', port_nums[0], Queue(), threading.Lock())
        server2 = MessageServer('localhost', port_nums[1], Queue(), threading.Lock())
        server3 = MessageServer('localhost', port_nums[2], Queue(), threading.Lock())

        # # Get all the machines to process queues
        # Process(target=machine_operate, args=(server1, port_nums, random.randint(1, 6), 1)).start()
        # Process(target=machine_operate, args=(server2, port_nums, random.randint(1, 6), 2)).start()
        # Process(target=machine_operate, args=(server3, port_nums, random.randint(1, 6), 3)).start()
        Process(target=machine_operate, args=(server1, port_nums, 1, 1, upper_random_num)).start()
        Process(target=machine_operate, args=(server2, port_nums, 3, 2, upper_random_num)).start()
        Process(target=machine_operate, args=(server3, port_nums, 6, 3, upper_random_num)).start()

        time.sleep(60)

        server1.close()
        server2.close()
        server3.close()
    except KeyboardInterrupt:
        server1.close()
        server2.close()
        server3.close()
        sys.exit(0)
