import subprocess
from hop import Stream
from hop.auth import Auth
from hop import auth
from hop.io import StartPosition
from hop.models import GCNCircular
import argparse
import random
import threading
import time
from functools import wraps
import datetime
import numpy
import uuid
from dotenv import load_dotenv
import os

from unittest.mock import Mock
import unittest
from mongoengine import connect, disconnect

# from hypothesis import given
# from hypothesis.strategies  import lists, integers


# from hop.apps.SNalert import model as M
# from hop.apps.SNalert import decider
# from hop.apps.SNalert import db_storage
# from . import demo
# from .. import test_anything

test_locations = ["Houston", "New York", "Boston", "Not Texas"]

# load environment variables
load_dotenv(dotenv_path='./../.env')

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
    """
    Produce exponential distribution data.
    :param mean: Mean of exponential distribution.
    :return:
    """
    return numpy.random.exponential(mean)


class integrationTest(object):
    # @given(
    #     timeout=integers(min_value=1),
    #     mean=integers(min_value=1),
    #     totalTime=integers(min_value=1)
    # )
    def __init__(self, timeout, mean, totalTime):
        """
        The constructor.
        :param timeout: Time expiration parameter
        :param mean:
        :param totalTime:
        """
        self.count = 0
        self.topic = os.getenv("OBSERVATION_TOPIC")
        self.mean = mean
        self.totalTime = totalTime
        # self.minTime = min
        # self.maxTime = max
        self.timeOut = timeout

        self.auth = Auth(os.getenv("USERNAME"), os.getenv("PASSWORD"), method=auth.SASLMethod.PLAIN)

    def run(self):
        """
        Run the model for the integration test.
        :return: none
        """
        t1 = threading.Thread(target=self.readNumMsg, args=(self.topic,))
        t1.start()

        m = subprocess.Popen(['python3',
                              '../hop/apps/SNalert/model.py',
                              '--f',
                              './../config.env',
                              '--no-auth'
                              ])

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
            now = datetime.datetime.utcnow().strftime(os.getenv("TIME_STRING_FORMAT"))
            # newFileName = self.writeMessage(now)
            stream = Stream(auth=self.auth)
            with stream.open(os.getenv("TESTING_TOPIC"), "w") as s:
                s.write(self.writeMessage(now))

        m.kill()

    def readNumMsg(self, topic):
        """
        Read the number of alert messages.
        :param topic:
        :param configFilePath:
        :return:
        """
        # gcnFormat = "json"
        stream = Stream(persist=True, auth=self.auth)
        # print("===")
        # print(topic)
        with stream.open(topic, "r") as s:
            for msg in s:  # set timeout=0 so it doesn't stop listening to the topic
                print("====")
                # if gcn_dict['header']['subject'] == "TEST":
                #     self.count += 1
                self.count += 1

    def getCount(self):
        return self.count

    def writeMessage(self, time):
        msg = {}
        msg["header"] = {}
        msg["header"]["MESSAGE ID"] = str(uuid.uuid4())
        msg["header"]["DETECTOR"] = "Test Detector"
        msg["header"]["SUBJECT"] = "Test"
        msg["header"]["MESSAGE SENT TIME"] = time
        msg["header"]["NEUTRINO TIME"] = time
        msg["header"]["LOCATION"] = test_locations[random.randint(0, 3)]
        msg["header"]["P VALUE"] = "0.5"
        msg["header"]["STATUS"] = "On"
        msg["header"]["MESSAGE TYPE"] = "Observation"
        msg["header"]["FROM"] = "Skylar Xu  <yx48@rice.edu>"
        msg["body"] = "This is an alert message generated at run time for testing purposes."
        return msg


# def functionalTest():
#
#     pass


class latencyTest(object):
    def __init__(self, topic, numDetector=50, time=3000):
        """
        The constructor.
        """
        self.numMsgPublished = 0
        self.numMsgReceived = 0
        self.totalLatency = 0
        self.numDetector = numDetector
        self.detectorThreads = {}
        self.countMsg = {}
        self.totalTime = time
        self.topic = topic
        self.auth = Auth(os.getenv("USERNAME"), os.getenv("PASSWORD"), method=auth.SASLMethod.PLAIN)
        self.idsWritten = set()
        self.idsReceived = set()

        self.lock = threading.Lock()

    def oneDetectorThread(self, uuid):
        # lock = threading.Lock()
        print(uuid)
        # print(timeout)
        startTime = time.monotonic()
        # randomly publish messages
        while time.monotonic() - startTime < self.totalTime:
            # print(time.monotonic() - startTime)
            # print(self.totalTime)
            # msg = self.writeMessage(uuid)
            stream = Stream(auth=self.auth)
            with stream.open(self.topic, "w") as s:
                msg = self.writeMessage(uuid)
                s.write(msg)
                with self.lock:
                    self.numMsgPublished += 1
                    self.idsWritten.add(msg["header"]["MESSAGE ID"])

    # def countWrittenMsgThread(self):

    def runTest(self):
        """
        Run the latency test.
        :return:
        """
        # create the topic if doesn't exist
        stream = Stream(auth=self.auth)
        # with stream.open(self.topic, "w") as s:
        #     s.write({"TEST": "TEST"})

        # first run the thread that logs every message received
        logThread = threading.Thread(target=self.logMsgs)
        logThread.start()

        # wait a few seconds
        startTime = time.monotonic()
        # randomly publish messages
        while time.monotonic() - startTime < 10:
            foo = 1

        for i in range(self.numDetector):
            # print(i)
            id = uuid.uuid4()
            # print(id)
            t = threading.Thread(target=self.oneDetectorThread, args=(str(id),))
            # self.oneDetectorThread(id)
            self.detectorThreads[id] = t
            t.start()

        # # first run the thread that logs every message received
        # logThread = threading.Thread(target=self.logMsgs)
        # logThread.start()

    def countMsgThread(self, msg_dict):
        """
        A single thread for process the message received for Latency test.
        :param msg_dict:
        :return:
        """
        # msg_dict = msg.asdict()['content']
        id = msg_dict['header']['DETECTOR']
        msg_id = msg_dict["header"]["MESSAGE ID"]
        receivedTime = datetime.datetime.utcnow().strftime(os.getenv("TIME_STRING_FORMAT"))
        sentTime = msg_dict['header']['MESSAGE SENT TIME']
        timeDiff = datetime.datetime.strptime(receivedTime, os.getenv(
            "TIME_STRING_FORMAT")) - datetime.datetime.strptime(sentTime, os.getenv("TIME_STRING_FORMAT"))
        timeDiff_inSeconds = timeDiff.total_seconds()
        # print("HERE")
        with self.lock:
            # print("____")
            self.numMsgReceived += 1
            self.totalLatency += timeDiff_inSeconds
            self.idsReceived.add(msg_id)

    def logMsgs(self):
        # stream = Stream(persist=True, auth=self.auth, start_at=StartPosition.EARLIEST)
        stream = Stream(persist=True, auth=self.auth)
        with stream.open(self.topic, "r") as s:
            for msg in s:  # set timeout=0 so it doesn't stop listening to the topic
                t = threading.Thread(target=self.countMsgThread, args=(msg.asdict()['content'],))
                t.start()

    def calculateAvgLatency(self):
        """
        Calculate the latency.
        :return:
        """
        return self.totalLatency * 1.0 / self.numMsgReceived

    def writeMessage(self, detector_id):
        """
        Return a dictionary of the message in the required format.
        :param uuid:
        :return:
        """
        now = datetime.datetime.utcnow().strftime(os.getenv("TIME_STRING_FORMAT"))
        msg = {}
        msg["header"] = {}
        msg["header"]["MESSAGE ID"] = str(uuid.uuid4())
        msg["header"]["DETECTOR"] = detector_id
        msg["header"]["SUBJECT"] = "Test"
        msg["header"]["MESSAGE SENT TIME"] = now
        msg["header"]["NEUTRINO TIME"] = now
        msg["header"]["LOCATION"] = test_locations[random.randint(0, 3)]
        msg["header"]["P VALUE"] = "0.5"
        msg["header"]["STATUS"] = "On"
        msg["header"]["MESSAGE TYPE"] = "Latency Testing"
        msg["header"]["FROM"] = "Skylar Xu  <yx48@rice.edu>"
        msg["body"] = "This is an alert message generated at run time for testing message latency."
        return msg

    def check(self):
        assert self.numMsgReceived == self.numMsgPublished


if __name__ == '__main__':

    print("Latency Test")
    print("----------------------------------------")
    print("Integration Test #1")
    test = latencyTest("kafka://dev.hop.scimma.org:9092/snews-latencyTest", 5, 50)
    print(test.totalTime)
    test.runTest()
    print("------")
    startTime = time.monotonic()
    # randomly publish messages
    while time.monotonic() - startTime < 100:
        foo = 1
        # print(time.monotonic() - startTime)
    print(test.calculateAvgLatency())
    print("     %d messages written." % test.numMsgPublished)
    print("     %d messages received and read." % test.numMsgReceived)
    # print("     %d messages written." % len(test.idsWritten))
    # print("     %d messages received and read." % len(test.idsReceived))
    # print("     %d messages read in written." % len(test.idsReceived.intersection(test.idsWritten)))
    assert test.numMsgPublished == test.numMsgReceived
