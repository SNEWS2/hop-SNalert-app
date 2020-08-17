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
import decider
import msgSchema
from pprint import pprint
import subprocess
import threading
from dataPacket import RegularDataPacket
import pickle
import time
import datetime
import jsonschema
from jsonschema import validate
from dotenv import load_dotenv
import dotenv
import os
import uuid

from hypothesis import given
from hypothesis.strategies  import lists, integers


# https://github.com/scimma/may2020-techthon-demo/blob/master/hop/apps/email/example.py
def _add_parser_args(parser):
    """Parse arguments for broker, configurations and options
    """
    # All args from the subscriber
    subscribe._add_parser_args(parser)

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
        # print("--------")
        print(type(os.getenv("NEW_DATABASE")))
        self.myDecider = decider.Decider(int(os.getenv("TIMEOUT")), os.getenv("TIME_STRING_FORMAT"), os.getenv("DATABASE_SERVER"), self.drop_db)
        self.deciderUp = False

        # self.auth = Auth("snews", "afe3.sl!f9a", method=auth.SASLMethod.PLAIN)

        self.regularMsgSchema = msgSchema.regularMsgSchema

        # m = threading.Thread(target=self.run)


        if args.default_authentication in ('True', 'T', 't', 'true', 'TRUE', 'Yes', 'yes', 'Y', 'y'):
            self.default_auth = True
        else:
            self.default_auth = False
        # print(args.drop_db)
        # print(type(args.default_authentication))
        if self.default_auth == False:
            username = os.getenv("USERNAME")
            password = os.getenv("PASSWORD")
            self.auth = Auth(username, password, method=auth.SASLMethod.PLAIN)
        self.experiment_topic = os.getenv("OBSERVATION_TOPIC")
        self.testing_topic = os.getenv("TESTING_TOPIC")
        self.heartbeat_topic = os.getenv("HEARTBEAT_TOPIC")


        # # Ask for heartbeat message once the decider is up
        # # while True:
        # #     if self.deciderUp:
        # #         break
        # h = threading.Thread(target=self.sendHeartbeatMessage)
        # h.start()

        self.run()


    def run(self):
        """
        Execute the model.
        :return: none
        """
        stream = Stream(persist=True, auth=self.auth)
        with stream.open(self.testing_topic, "r") as s:
            self.deciderUp = True
            for msg in s:  # set timeout=0 so it doesn't stop listening to the topic
                # print(type(gcn_dict))
                # print(prepare_gcn(gcn_dict))
                print("--THE MODEL")
                msg_dict = msg.asdict()['content']
                print(msg_dict)
                print(type(msg_dict))
                print(msg_dict['header']['SUBJECT'])
                self.processMessage(msg_dict)
                print("--THE MODEL")
                print("")


    def add_gcn(self, gcn):
        """
        Initial alert model upon receiving published information.
        """
        sent_time = gcn['header']['MESSAGE SENT TIME']
        neutrino_time = gcn['header']['NEUTRINO TIME']
        # sent_time = gcn['header']['date']
        # neutrino_time = gcn['header']['date']

        message = gcn['body']
        # print("---")
        # print(type(message))
        self.myDecider.addMessage(sent_time, neutrino_time, gcn)


    def processMessage(self, message):
        # if heartbeat message do sth

        # if regular msg, do sth

        self.processRegularMessage(message)


    def processRegularMessage(self, message):
        """
        Process an observation message from experiments.
        :param message:
        :return: none
        """
        # verify the schema
        isValid = validateJson(message, self.regularMsgSchema)
        if isValid == True:
            self.add_gcn(message)
            alert = self.myDecider.deciding()
            print("-- Model ???????")
            for i in self.myDecider.getCacheMessages():
                print(i)
            print("-- Model ???????")
            if alert == True:
                # publish to TOPIC2 and alert astronomers
                stream = Stream(auth=self.auth)
                with stream.open(self.experiment_topic, "w") as s:
                    s.write(self.writeAlertMsg())

        # else:
        #     # alert the experiment of the wrong message format


    def sendHeartbeatMessage(self):
        while True:
            if self.deciderUp:
                stream = Stream(auth=self.auth)
                with stream.open(self.heartbeat_topic, "w") as s:
                    s.write(self.writeRequestHeartbeatMsg())
            time.sleep(10)


    # def sendRegularMessage(self):
    #     with open(self.args.temp_gcnfile_path,'r') as f:
    #         m = RegularDataPacket.RegularDataPacket(self, f)
    #         publish_process = subprocess.Popen(['hop',
    #                                             'publish',
    #                                             'kafka://dev.hop.scimma.org:9092/snews-experiments',
    #                                             '-F',
    #                                             self.args.f,
    #                                             m])
    #         pickle.dump(m, )

    def generateAlertMsg(self):
        time = datetime.datetime.utcnow()
        fileName = time.strftime("%y/%m/%d%H:%M:%S")
        pass
    
    # def sendOutEmails(self):
    #     pass

    def writeAlertMsg(self):
        msg = {}
        msg["header"] = {}
        msg["header"]["MESSAGE ID"] = str(uuid.uuid4())
        msg["header"]["SUBJECT"] = "Test Alert"
        msg["header"]["MESSAGE SENT TIME"] = datetime.datetime.utcnow().strftime(os.getenv("TIME_STRING_FORMAT"))
        msg["header"]["LOCATION"] = "Houston"
        msg["header"]["STATUS"] = "On"
        msg["header"]["MESSAGE TYPE"] = "TEST"
        msg["header"]["FROM"] = "Skylar Xu  <yx48@rice.edu>"
        msg["body"] = "This is an alert message generated at run time for testing purposes."
        return msg

    def writeRequestHeartbeatMsg(self):
        msg = {}
        msg["header"] = {}
        msg["header"]["MESSAGE ID"] = str(uuid.uuid4())
        msg["header"]["SUBJECT"] = "Test Heartbeat"
        msg["header"]["MESSAGE SENT TIME"] = datetime.datetime.utcnow().strftime(os.getenv("TIME_STRING_FORMAT"))
        msg["header"]["LOCATION"] = "Houston"
        msg["header"]["STATUS"] = "On"
        msg["header"]["MESSAGE TYPE"] = "Heartbeat"
        msg["header"]["FROM"] = "Skylar Xu  <yx48@rice.edu>"
        msg["body"] = "This is an alert message generated at run time for testing purposes."
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
    # parser.add_argument('--t', type=int, metavar='N',
    #                     help='The time period where observations of a supernova could occur. unit: seconds')
    # parser.add_argument('--time-format', type=str, metavar='N',
    #                     help='The format of the time string in all messages.')
    # parser.add_argument('--emails-file', type=str, metavar='N',
    #                     help='Send alerts to these emails upon possible SN.')
    # parser.add_argument('--mongo-server', type=str, metavar='N',
    #                     help='The MongoDB server to be used.')
    # parser.add_argument('--drop-db', type=str, metavar='N',
    #                     help='Whether to drop and restart a database or not.')
    
    ## FORMAL ENVIRONMENTAL VARIABLES
    # parser.add_argument('--username', type=str, metavar='N',
    #                     help='The credential for Hopskotch. If not specified, look for the default file under .config/hop')
    # parser.add_argument('--password', type=str, metavar='N',
    #                     help='The credential for Hopskotch. If not specified, look for the default file under .config/hop')
    parser.add_argument('--f', type=str, metavar='N',
                        help="The path to the .env file.")
    parser.add_argument('--default-authentication', type=str,
                        help='Whether to use local ~/.config/hop-client/config.toml file or not.')
    args = parser.parse_args()

    # model = Model(args)
    main(args)



