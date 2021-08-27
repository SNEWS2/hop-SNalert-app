"""
hop subscribe class
for the SNEWS member experiments (also others?)
to subscribe and listen to the alert topics

# Author: 
Sebastian Torres-Lara, Univ of Houston
Melih Kara kara@kit.edu

"""

# Imports
import snews_utils
from hop import Stream
from pathlib import Path
import os
from collections import namedtuple


class HopSubscribe:
    def __init__(self, env):
        self.time_stuff = snew_util.TimeStuff(env)
        self.hr = self.time_stuff.get_hr_str()
        self.date = self.time_stuff.get_date_str()
        self.snews_time = self.time_stuff.get_snews_time_str()

    def save_mgs(self, topic, message, date):
        id = message['message_id']
        path = f'SNEWS_MSGs/{topic}/{date}'
        snews_utils.make_dir(path)
        text_file = open(f"{path}/{id}.txt", "w+")
        text_file.write(str(message))
        text_file.close()

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