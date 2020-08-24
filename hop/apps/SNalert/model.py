#!/usr/bin/env python

import argparse
import datetime
import os
import random
import smtplib
import sys
import time
import uuid

from dotenv import load_dotenv
import jsonschema
from jsonschema import validate
import numpy

from hop import Stream
from hop import auth
from hop import cli
from hop import subscribe
from hop.auth import Auth

from . import decider
from . import msgSchema
from .dataPacket.observationMsg import SNEWSObservation
from .dataPacket.heartbeatMsg import SNEWSHeartbeat
from .dataPacket.alertMsg import SNEWSAlert


def _add_parser_args(parser):
    """Parse arguments for broker, configurations and options
    """
    # Add general client args
    cli.add_client_opts(parser)

    ## FORMAL ENVIRONMENTAL VARIABLES
    # parser.add_argument('--username', type=str, metavar='N',
    #                     help='The credential for Hopskotch. If not specified, look for the default file under .config/hop')
    # parser.add_argument('--password', type=str, metavar='N',
    #                     help='The credential for Hopskotch. If not specified, look for the default file under .config/hop')
    parser.add_argument('-f', '--env-file', type=str, help="The path to the .env file.")
    parser.add_argument('--use-default-auth', action="store_true",
                        help='If set, use local ~/.config/hop-client/config.toml file to authenticate.')


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
        load_dotenv(dotenv_path=args.env_file)

        self.args = args
        self.gcnFormat = "json"
        self.drop_db = bool(os.getenv("NEW_DATABASE"))
        self.myDecider = decider.Decider(int(os.getenv("TIMEOUT")), os.getenv("TIME_STRING_FORMAT"), os.getenv("DATABASE_SERVER"), self.drop_db)
        self.deciderUp = False
        self.regularMsgSchema = msgSchema.regularMsgSchema

        # configure authentication
        if args.no_auth:
            self.auth = False
        elif not args.use_default_auth:
            username = os.getenv("USERNAME")
            password = os.getenv("PASSWORD")
            self.auth = Auth(username, password, method=auth.SASLMethod.PLAIN)
        else:
            self.auth = True

        # specify topics
        self.experiment_topic = os.getenv("OBSERVATION_TOPIC")
        self.testing_topic = os.getenv("TESTING_TOPIC")
        self.heartbeat_topic = os.getenv("HEARTBEAT_TOPIC")
        self.alert_topic = os.getenv("ALERT_TOPIC")

        # message types and processing algorithms
        self.mapping = {
            SNEWSObservation.__name__: self.processObservationMessage,
            SNEWSHeartbeat.__name__: self.processHearbeatMessage
        }


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
        stream = Stream(persist=True, auth=self.auth)
        with stream.open(self.testing_topic, "r") as s:
            self.deciderUp = True
            for msg in s:
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
        if alert:
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


def main(args):
    """main function
    """
    model = Model(args)
    model.run()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    _add_parser_args(parser)
    args = parser.parse_args()

    main(args)
