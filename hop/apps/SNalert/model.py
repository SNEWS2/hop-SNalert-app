#!/usr/bin/env python

import smtplib
import argparse
import json
from hop import Stream
from hop import auth
from hop.auth import Auth
from hop.models import GCNCircular
from hop import subscribe
import sys
from pprint import pprint
import subprocess
import threading
import pickle
import time
import datetime
import jsonschema
from jsonschema import validate
from dotenv import load_dotenv
import dotenv
import os
import uuid

import numpy
import random

from . import decider
from . import msgSchema
from .dataPacket.observationMsg import SNEWSObservation
from .dataPacket.heartbeatMsg import SNEWSHeartbeat
from .dataPacket.alertMsg import SNEWSAlert


# https://github.com/scimma/may2020-techthon-demo/blob/master/hop/apps/email/example.py
def _add_parser_args(parser):
    """Parse arguments for broker, configurations and options
    """
    # All args from the subscriber
    subscribe._add_parser_args(parser)

    ## FORMAL ENVIRONMENTAL VARIABLES
    # parser.add_argument('--username', type=str, metavar='N',
    #                     help='The credential for Hopskotch. If not specified, look for the default file under .config/hop')
    # parser.add_argument('--password', type=str, metavar='N',
    #                     help='The credential for Hopskotch. If not specified, look for the default file under .config/hop')
    parser.add_argument('--f', type=str, metavar='N',
                        help="The path to the .env file.")
    parser.add_argument('--default-authentication', type=str,
                        help='Whether to use local ~/.config/hop-client/config.toml file or not.')


# https://github.com/scimma/may2020-techthon-demo/blob/master/hop/apps/email/example.py
def prepare_gcn(gcn_dict, json_dump=False):
    """Parse a gcn dictionary and print to stdout.
    Args:
      gcn_dict:  the dictionary object containing a GCN-formatted message
    Returns:
      None
    """
    if json_dump:
        return (json.dumps(gcn_dict))
    else:
        gcn = GCNCircular(**gcn_dict)
        message = ""
        for line in str(gcn).splitlines():
            message += line + "\n"
        return message


# verify json
def validateJson(jsonData, jsonSchema):
    """
    Function for validate a json data using a json schema.
    :param jsonData: the data to validate.
    :param jsonSchema: the schema assumed to be correct.
    :return: true or false
    """
    try:
        validate(instance=jsonData, schema=jsonSchema)
    except jsonschema.exceptions.ValidationError as err:
        return False
    return True


class Model(object):
    def __init__(self, args):
        """
        The constructor of the model class.
        :param args: the command line arguments
        """
        # load environment variables
        load_dotenv(dotenv_path=args.f)

        self.args = args
        self.gcnFormat = "json"
        if os.getenv("NEW_DATABASE") in ('True', 'T', 't', 'true', 'TRUE', 'Yes', 'yes', 'Y', 'y'):
            self.drop_db = True
        else:
            self.drop_db = False
        self.myDecider = decider.Decider(int(os.getenv("TIMEOUT")), os.getenv("TIME_STRING_FORMAT"), os.getenv("DATABASE_SERVER"), self.drop_db)
        self.deciderUp = False

        # self.auth = Auth("snews", "afe3.sl!f9a", method=auth.SASLMethod.PLAIN)

        self.regularMsgSchema = msgSchema.regularMsgSchema

        # m = threading.Thread(target=self.run)


        if args.default_authentication in ('True', 'T', 't', 'true', 'TRUE', 'Yes', 'yes', 'Y', 'y'):
            self.default_auth = True
        else:
            self.default_auth = False
        if self.default_auth == False:
            username = os.getenv("USERNAME")
            password = os.getenv("PASSWORD")
            self.auth = Auth(username, password, method=auth.SASLMethod.PLAIN)
        self.experiment_topic = os.getenv("OBSERVATION_TOPIC")
        self.testing_topic = os.getenv("TESTING_TOPIC")
        self.heartbeat_topic = os.getenv("HEARTBEAT_TOPIC")
        self.alert_topic = os.getenv("ALERT_TOPIC")

        # message types and processing algorithms
        self.mapping = {
            SNEWSObservation.__name__: self.processObservationMessage,
            SNEWSHeartbeat.__name__: self.processHearbeatMessage
        }

        self.run()


    # def writeCustomMsg(self):
    #     while True:
    #         stream = Stream(auth=self.auth)
    #
    #         obsMsg = SNEWSObservation(str(uuid.uuid4()),
    #                                 "DETECTOR 1",
    #                                 datetime.datetime.utcnow().strftime(os.getenv("TIME_STRING_FORMAT")),
    #                                 datetime.datetime.utcnow().strftime(os.getenv("TIME_STRING_FORMAT")),
    #                                 datetime.datetime.utcnow().strftime(os.getenv("TIME_STRING_FORMAT")),
    #                                 test_locations[random.randint(0, 3)],
    #                                 "0.5",
    #                                 "On",
    #                                 "For testing")
    #
    #         with stream.open(os.getenv("TESTING_TOPIC"), "w") as s:
    #             s.write(obsMsg)

    def run(self):
        """
        Execute the model.
        :return: none
        """
        # t = threading.Thread(target=self.writeCustomMsg)
        # t.start()

        stream = Stream(persist=True, auth=self.auth)
        with stream.open(self.testing_topic, "r") as s:
            self.deciderUp = True
            for msg in s:  # set timeout=0 so it doesn't stop listening to the topic
                self.processMessage(msg)

    def addObservationMsg(self, message):
        self.myDecider.addMessage(message)

    def processMessage(self, message):
        message_type = type(message).__name__
        if message_type in self.mapping:
            self.mapping[message_type](message)

    def processObservationMessage(self, message):
        self.addObservationMsg(message)
        alert = self.myDecider.deciding()
        if alert == True:
            # publish to TOPIC2 and alert astronomers
            stream = Stream(auth=self.auth)
            with stream.open(self.alert_topic, "w") as s:
                s.write(self.writeAlertMsg())

    def processHearbeatMessage(self, message):
        pass
    
    # def sendOutEmails(self):
    #     pass

    def writeAlertMsg(self):
        msg = SNEWSAlert(str(uuid.uuid4()),
                       datetime.datetime.utcnow().strftime(os.getenv("TIME_STRING_FORMAT")),
                       datetime.datetime.utcnow().strftime(os.getenv("TIME_STRING_FORMAT")),
                       "Supernova Alert")
        return msg


# ------------------------------------------------
# -- main
def main(args):
    """main function
    """
    model = Model(args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    _add_parser_args(parser)
    args = parser.parse_args()

    main(args)
