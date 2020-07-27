import subprocess
from hop import stream
from hop.models import GCNCircular
import argparse
import random
import threading
import time
from functools import wraps
import datetime
import numpy

from unittest.mock import Mock
import unittest
from mongoengine import connect, disconnect

# from ..hop.apps.SNalert import model as M
# from ..hop.apps.SNalert import decider
# from ..hop.apps.SNalert import db_storage
# from . import demo
# from .. import test_anything

test_locations = ["Houston", "New York", "Boston", "Not Texas"]

# for measuring function execution time
# https://stackoverflow.com/questions/3620943/measuring-elapsed-time-with-the-time-module
PROF_DATA = {}

def profile(fn):
    @wraps(fn)
    def with_profiling(*args, **kwargs):
        start_time = time.time()

        ret = fn(*args, **kwargs)

        elapsed_time = time.time() - start_time

        if fn.__name__ not in PROF_DATA:
            PROF_DATA[fn.__name__] = [0, []]
        PROF_DATA[fn.__name__][0] += 1
        PROF_DATA[fn.__name__][1].append(elapsed_time)

        return ret

    return with_profiling

def print_prof_data():
    for fname, data in PROF_DATA.items():
        max_time = max(data[1])
        avg_time = sum(data[1]) / len(data[1])
        print("Function %s called %d times. " % (fname, data[0]))
        print('Execution time max: %.3f, average: %.3f' % (max_time, avg_time))

def clear_prof_data():
    global PROF_DATA
    PROF_DATA = {}



def exponentialDistribution(mean):
    return numpy.random.exponential(mean)

class integrationTest(object):
    def __init__(self, timeout, mean, totalTime, min, max):
        self.count = 0
        self.topic = "kafka://dev.hop.scimma.org:9092/snews-experiments"
        self.configF = "../utils/config.conf"
        self.mean = mean
        self.totalTime = totalTime
        self.minTime = min
        self.maxTime = max
        self.timeOut = timeout

    def run(self):
        t1 = threading.Thread(target=self.readNumMsg, args={self.topic, self.configF})
        t1.start()

        m = subprocess.Popen(['python3',
                              '../hop/apps/SNalert/model.py',
                              '--f',
                              self.configF,
                              '--t',
                              str(self.timeOut),
                              '--time-format',
                              '%y/%m/%d %H:%M:%S',
                              '--temp-gcnfile-path',
                              './../utils/messages/unitTest.gcn3',
                              '--mongo-server',
                              'mongodb://localhost:27017/',
                              '--drop-db',
                              'True',
                              '--heartbeat-path',
                              '../hop/apps/SNalert/dataPacket/heartbeatMsg.gcn3'])

        startTime = time.monotonic()
        # randomly publish messages
        while time.monotonic() - startTime < self.totalTime:
            # randomTime = random.randint(self.minTime, self.maxTime)
            randomTime = exponentialDistribution(self.mean)
            start2 = time.monotonic()
            while True:
                if time.monotonic() - start2 > randomTime:
                    break
            # write message with current time
            now = datetime.datetime.utcnow().strftime("%y/%m/%d %H:%M:%S")
            newFileName = self.writeMessage(now)
            experiment = subprocess.call(['hop',
                                          'publish',
                                          'kafka://dev.hop.scimma.org:9092/snews-testing',
                                          '-F',
                                          self.configF,
                                          newFileName])

        m.kill()

    def readNumMsg(self, topic, configFilePath):
        # p = subprocess.Popen(["hop",
        #                       "subscribe",
        #                       topic,
        #                       "-F",
        #                       configFilePath,
        #                       "-t",
        #                       "0"])
        gcnFormat = "json"
        with stream.open(topic, "r", config=configFilePath,
                         format=gcnFormat) as s:
            for gcn_dict in s(timeout=0):  # set timeout=0 so it doesn't stop listening to the topic
                print("====")
                # print(gcn_dict)
                # print(gcn_dict['SUBJECT'])
                # print(self.count)
                # print('')
                # if gcn_dict['header']['subject'] == "TEST":
                #     self.count += 1
                self.count += 1

    def getCount(self):
        return self.count

    def writeMessage(self, time):
        time2 = time.replace(' ', '-').replace('/', '').replace(':','')
        fileName = "../utils/messages/integrationTest/" + time2 + ".gcn3"
        with open(fileName, 'w') as f:
            f.write("TITLE:   GCN CIRCULAR\n")
            f.write("NUMBER:  SOME NUMBER\n")
            f.write("SUBJECT: TEST\n")
            f.write("DATE:    ")
            f.write(time)
            # f.write("P VALUE: 0.5\n")
            f.write("\n")
            f.write("FROM:    Skylar Xu  <yx48@rice.edu>\n")
            f.write("\n")
            f.write("This is a message generated at run time for testing purposes.\n")

            # f.write("DETECTOR NAME:     TEST DETECTOR\n")
            # f.write("SUBJECT:       Test\n")
            # f.write("MESSAGE SENT TIME:     ")
            # f.write(time)
            # f.write("\n")
            # f.write("NEUTRINO TIME:     ")
            # f.write(time)
            # f.write("\n")
            # f.write("LOCATION:      ")
            # f.write("%s" % test_locations[random.randint(0, 3)])
            # f.write("P VALUE: 0.5\n")
            # f.write("STATUS:  ON\n")
            # f.write("MESSAGE TYPE:      TEST\n")
            # f.write("FROM:    Skylar Xu  <yx48@rice.edu>\n")
            # f.write("\n")
            # f.write("This is a message generated at run time for testing purposes.")
        return fileName

def unitTest():
    pass


def functionalTest():

    pass


def testLatency():
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    # # temporary. May switch to subscribe(parser) later
    # parser.add_argument('--f', type=str, metavar='N',
    #                     help='The configuration file.')
    # args = parser.parse_args()

    print("Perform Integration Testing:")
    # run a model
    # m1 = subprocess.Popen(["python3",
    #                        "../hop/app/SNalert/model.py"])
    print("----------------------------------------")
    print("Integration Test #1")
    print("     Frequency of SNs:  ")
    test1 = integrationTest(10, 20, 600, 2, 38)
    test1.run()
    print("     The number of concidences:  %d" % test1.getCount())