"""
hop subscribe class
for the SNEWS member experiments (also others?)
to subscribe and listen to the alert topics

# Author: 
Sebastian Torres-Lara, Univ of Houston
Melih Kara kara@kit.edu

Notes
https://docs.python.org/3/howto/logging.html

"""

# Imports
import snews_utils
from hop import Stream
from pathlib import Path
import os
from collections import namedtuple


class HopSubscribe:
    def __init__(self, env):
        snews_utils.set_env(env_path)
        self.broker            = os.getenv("HOP_BROKER")
        self.observation_topic = os.getenv("OBSERVATION_TOPIC") # only snews can subscribe
        self.alert_topic       = os.getenv("ALERT_TOPIC")

        # time object/strings
        self.times = snews_utils.TimeStuff(env_path)
        self.hr = self.times.get_hour()
        self.date = self.times.get_date()
        self.snews_time = self.times.get_snews_time()


    def save_mgs(self, topic, message, date):
        id = message['message_id']
        path = f'SNEWS_MSGs/{topic}/{date}'
        snews_utils.make_dir(path)
        logger = snews_utils.get_logger('hopsub', path+'loggings.log')
        logger.info(str(message))
        # text_file = open(f"{path}/{id}.txt", "w+")
        # text_file.write(str(message))
        # text_file.close()

    def topic_sub(self, which_topic):
        # set topic enum, get name and broker
        topic = snew_util.set_topic_state(which_topic)
        name = topic.topic_name
        broker = topic.topic_broker
        print(f'Subscribing to {name} Topic\nBroker:{broker}')
        # Initiate hop_stream
        stream = Stream(persist=True)
        with stream.open(broker, "r") as s:
            for message in s:
                print(f"{name} from {message['detector_id']}")