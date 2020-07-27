#!/usr/bin/env python

import smtplib
import argparse
import json
from hop import stream
from hop.models import GCNCircular
# from hop import cli
from hop import subscribe
import sys
# import decider_deque
import decider
from pprint import pprint
import subprocess
import threading
from dataPacket import RegularDataPacket
import pickle
import time
import datetime
import jsonschema
from jsonschema import validate


# https://github.com/scimma/may2020-techthon-demo/blob/master/hop/apps/email/example.py
def _add_parser_args(parser):
    """Parse arguments for broker, configurations and options
    """
    # All args from the subscriber
    # subscribe._add_parser_args(parser)

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
    try:
        validate(instance=jsonData, schema=jsonSchema)
    except jsonschema.exceptions.ValidationError as err:
        return False
    return True


class Model(object):
    def __init__(self, args):
        self.args = args
        self.gcnFormat = "json"
        # if args.drop_db == "t":
        #     self.dropDB = True
        # else:
        #     self.dropDB = False
        self.myDecider = decider.Decider(args.t, args.time_format,args.mongo_server, args.drop_db)
        self.deciderUp = False
        # self.heartbeatMsgPath = "dataPacket/heartBeatMsg.gcn3"
        self.heartbeatMsgPath = args.heartbeat_path

        self.regularMsgSchema = {
            "type": "object",
            "properties": {
                "header": {
                    "type": 'object',
                    "properties": {
                        "title": {"type": "string"},
                        "number": {"type": "string"},
                        "subject": {"type": "string"},
                        "date": {"type": "string"},
                        "from": {"type": "string"}
                    }
                },
                "body": {"type": "string"}
            }
        }

        # m = threading.Thread(target=self.run)

        # Ask for heartbeat message once the decider is up
        # while True:
        #     if self.deciderUp:
        #         break
        h = threading.Thread(target=self.sendHeartbeatMessage)
        h.start()
        self.run()


    def run(self):
        with stream.open("kafka://dev.hop.scimma.org:9092/snews-testing", "r", config=self.args.f, format=self.gcnFormat) as s:
            self.deciderUp = True
            for gcn_dict in s(timeout=0):  # set timeout=0 so it doesn't stop listening to the topic
                # print(type(gcn_dict))
                # print(prepare_gcn(gcn_dict))
                print("--THE MODEL")
                print(gcn_dict)
                print(gcn_dict['header']['subject'])
                self.processMessage(gcn_dict)
                print("--THE MODEL")
                print("")


    def add_gcn(self, gcn):
        """
        Initial alert model upon receiving published information.
        """
        # sent_time = gcn['header']['message sent time']
        # neutrino_time = gcn['header']['neutrino time']
        sent_time = gcn['header']['date']
        neutrino_time = gcn['header']['date']

        message = gcn['body']
        # print("---")
        # print(type(message))
        self.myDecider.addMessage(sent_time, neutrino_time, gcn)


    def processMessage(self, message):
        # if heartbeat message do sth

        # if regular msg, do sth

        self.processRegularMessage(message)


    def processRegularMessage(self, message):
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
                # print("hhhhhhhhhhhhhhhhhhhhhhhhhh")
                # publish to TOPIC2 and alert astronomers
                publish_process = subprocess.Popen(['hop',
                                                    'publish',
                                                    'kafka://dev.hop.scimma.org:9092/snews-experiments',
                                                    '-F',
                                                    self.args.f,
                                                    self.args.temp_gcnfile_path])
                # '../../../utils/messages/unitTest.gcn3'])
                # self.sendRegularMessage()
        # else:
        #     # alert the experiment of the wrong message format


    def sendHeartbeatMessage(self):
        while True:
            if self.deciderUp:
                hb_process = subprocess.Popen(['hop',
                                               'publish',
                                               'kafka://dev.hop.scimma.org:9092/snews-heartbeat',
                                               '-F',
                                               self.args.f,
                                               self.heartbeatMsgPath])
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
        fileName = time.strptime("%y/%m/%d%H:%M:%S")
        pass


# ------------------------------------------------
# -- main

# def _main(args=None):
#     """main function
#     """
#
#     if not args:
#         parser = argparse.ArgumentParser()
#         _add_parser_args(parser)
#
#         # temporary. May switch to subscribe(parser) later
#         parser.add_argument('--f', type=str, metavar='N',
#                             help='The configuration file.')
#         parser.add_argument('--t', type=int, metavar='N',
#                             help='The time period where observations of a supernova could occur. unit: seconds')
#         parser.add_argument('--time-format', type=str, metavar='N',
#                             help='The format of the time string in all messages.')
#         parser.add_argument('--temp-gcnfile-path', type=str, metavar='N',
#                             help='The temporary path to the gcn file published to all experiments. At later stage, generate this at run time.')
#         # parser.add_argument('--alert-url', type=str, metavar='N',
#         #                     help='The kafka url the every experiment listen to.')
#         # parser.add_argument('--emails-file', type=str, metavar='N',
#         #                     help='Send alerts to these emails upon possible SN.')
#         # parser.add_argument('--subscribe-topic', type=str, metavar='N',
#         #                     help='The topic that the decider listens to.')
#         # parser.add_argument('--publish-topic', type=str, metavar='N',
#         #                     help='The topic that the decider publishes to.')
#         parser.add_argument('--mongo-server', type=str, metavar='N',
#                             help='The MongoDB server to be used.')
#         parser.add_argument('--drop-db', type=bool, metavar='N',
#                             help='Whether to drop and restart a database or not.')
#         args = parser.parse_args()
#
#     # # load config if specified
#     # config = cli.load_config(args)
#     #
#     # # load consumer options
#     # start_offset = "earliest" if args.earliest else "latest"
#
#     gcn_format = "json"
#     # receivers = [email for email in args.email]
#
#     the_decider = decider.Decider(args.t, args.time_format,args.mongo_server, args.drop_db)
#
#     with stream.open("kafka://dev.hop.scimma.org:9092/snews-testing", "r", config=args.f, format=gcn_format) as s:
#         for gcn_dict in s(timeout=0): # set timeout=0 so it doesn't stop listening to the topic
#             # print(type(gcn_dict))
#             # print(prepare_gcn(gcn_dict))
#             print("--THE MODEL")
#             # pprint(type(gcn_dict))
#             add_gcn(gcn_dict, the_decider)
#             alert = the_decider.deciding()
#             if alert == True:
#                 # publish to TOPIC2 and alert astronomers
#                 # print("haha")
#                 publish_process = subprocess.Popen(['hop',
#                                                     'publish',
#                                                     'kafka://dev.hop.scimma.org:9092/snews-experiments',
#                                                     '-F',
#                                                     args.f,
#                                                     args.temp_gcnfile_path])
#                                                     # '../../../utils/messages/unitTest.gcn3'])
#             print("--THE MODEL")
#             print("")


# temporary
if __name__ == '__main__':
    # _main()
    parser = argparse.ArgumentParser()
    _add_parser_args(parser)

    # temporary. May switch to subscribe(parser) later
    parser.add_argument('--f', type=str, metavar='N',
                        help='The configuration file.')
    parser.add_argument('--t', type=int, metavar='N',
                        help='The time period where observations of a supernova could occur. unit: seconds')
    parser.add_argument('--time-format', type=str, metavar='N',
                        help='The format of the time string in all messages.')
    parser.add_argument('--temp-gcnfile-path', type=str, metavar='N',
                        help='The temporary path to the gcn file published to all experiments. At later stage, generate this at run time.')
    # parser.add_argument('--emails-file', type=str, metavar='N',
    #                     help='Send alerts to these emails upon possible SN.')
    # parser.add_argument('--subscribe-topic', type=str, metavar='N',
    #                     help='The topic that the decider listens to.')
    # parser.add_argument('--publish-topic', type=str, metavar='N',
    #                     help='The topic that the decider publishes to.')
    parser.add_argument('--mongo-server', type=str, metavar='N',
                        help='The MongoDB server to be used.')
    parser.add_argument('--drop-db', type=bool, metavar='N',
                        help='Whether to drop and restart a database or not.')
    parser.add_argument('--heartbeat-path', type=str, metavar='N',
                        help='The heartbeat message file.')
    args = parser.parse_args()

    model = Model(args)