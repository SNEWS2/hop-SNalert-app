#!/usr/bin/env python

import datetime
import logging
import os
import uuid

from dotenv import load_dotenv
import jsonschema
from jsonschema import validate

from hop import Stream
from hop.plugins.snews import SNEWSAlert, SNEWSHeartbeat, SNEWSObservation

from . import decider
from . import msgSchema


logger = logging.getLogger("snews")


def _add_parser_args(parser):
    """Parse arguments for broker, configurations and options
    """
    parser.add_argument('-v', '--verbose', action='count', default=0, help="Be verbose.")
    parser.add_argument('-f', '--env-file', type=str, help="The path to the .env file.")
    parser.add_argument("--no-auth", action="store_true", help="If set, disable authentication.")


def validateJson(jsonData, jsonSchema):
    """
    Function for validate a json data using a json schema.
    :param jsonData: the data to validate.
    :param jsonSchema: the schema assumed to be correct.
    :return: true or false
    """
    try:
        validate(instance=jsonData, schema=jsonSchema)
    except jsonschema.exceptions.ValidationError:
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
        self.coinc_threshold = int(os.getenv("COINCIDENCE_THRESHOLD"))
        self.msg_expiration = int(os.getenv("MSG_EXPIRATION"))
        self.db_server = os.getenv("DATABASE_SERVER")
        self.drop_db = bool(os.getenv("NEW_DATABASE"))
        self.regularMsgSchema = msgSchema.regularMsgSchema

        logger.info(f"setting up decider at: {self.db_server}")
        self.myDecider = decider.Decider(
            self.coinc_threshold,
            self.msg_expiration,
            os.getenv("TIME_STRING_FORMAT"),
            os.getenv("DATABASE_SERVER"),
            self.drop_db
        )
        if self.drop_db:
            logger.info("clearing out decider cache")
        self.deciderUp = False

        # specify topics
        self.observation_topic = os.getenv("OBSERVATION_TOPIC")
        self.alert_topic = os.getenv("ALERT_TOPIC")

        # open up stream connections
        self.stream = Stream(auth=(not args.no_auth), persist=True)
        self.source = self.stream.open(self.observation_topic, "r")
        self.sink = self.stream.open(self.alert_topic, "w")

        # message types and processing algorithms
        self.mapping = {
            SNEWSObservation.__name__: self.processObservationMessage,
            SNEWSHeartbeat.__name__: self.processHeartbeatMessage
        }

    def run(self):
        """
        Execute the model.
        :return: none
        """
        self.deciderUp = True
        logger.info("starting decider")
        logger.info(f"processing messages from {self.observation_topic}")
        for msg, meta in self.source.read(batch_size=1, metadata=True, autocommit=False):
            self.processMessage(msg)
            self.source.mark_done(meta)

    def close(self):
        """
        Close stream connections.
        """
        logger.info("shutting down")
        self.deciderUp = False
        self.source.close()
        self.sink.close()

    def addObservationMsg(self, message):
        self.myDecider.addMessage(message)

    def processMessage(self, message):
        message_type = type(message).__name__
        logger.debug(f"processing {message_type}")
        if message_type in self.mapping:
            self.mapping[message_type](message)

    def processObservationMessage(self, message):
        self.addObservationMsg(message)
        alert = self.myDecider.deciding()
        if alert:
            # publish alert message to ALERT_TOPIC
            logger.info("found coincidence, sending alert")
            self.sink.write(self.writeAlertMsg())

    def processHeartbeatMessage(self, message):
        pass

    def writeAlertMsg(self):
        return SNEWSAlert(
            message_id=str(uuid.uuid4()),
            sent_time=datetime.datetime.utcnow().strftime(os.getenv("TIME_STRING_FORMAT")),
            machine_time=datetime.datetime.utcnow().strftime(os.getenv("TIME_STRING_FORMAT")),
            content="SNEWS Alert: a coincidence between detectors has been observed.",
        )


def main(args):
    """main function
    """
    # set up logging
    verbosity = [logging.WARNING, logging.INFO, logging.DEBUG]
    logging.basicConfig(
        level=verbosity[min(args.verbose, 2)],
        format="%(asctime)s | model : %(levelname)s : %(message)s",
    )

    # start up
    model = Model(args)
    try:
        model.run()
    except KeyboardInterrupt:
        pass
    finally:
        model.close()
