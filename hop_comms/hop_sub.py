# Author: Sebastian Torres-Lara, Univ of Houston

# Imports
import snew_util
from hop import Stream
from pathlib import Path
import os
from collections import namedtuple


# make dir with current date
def make_dir(path):
    if Path(path).is_dir():
        pass
    else:
        os.makedirs(path)


"""
hop-subscribe class
"""


class HopSubscribe:
    def __init__(self, env):
        self.time_stuff = snew_util.TimeStuff(env)
        self.hr = self.time_stuff.get_hr_str()
        self.date = self.time_stuff.get_date_str()
        self.snews_time = self.time_stuff.get_snews_time_str()

    def save_mgs(self, topic, message,date):
        id = message['message_id']
        path = f'SNEWS_MSGs/{topic}/{date}'
        make_dir(path)
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




# #
# # a persistent stream to OBSERVATION_TOPIC,
# # sends OBS message to save_message_obs()
# # this was a testing method
# def sub_obs():
#     stream = Stream(persist=True)
#
#     with stream.open(set_topic("O"), "r") as s:
#         for message in s:
#             print(f"saw an OBS at: {hr_str()} {date_str()} from {message['detector_id']}")
#             save_message_obs(message, message['detector_id'])
#
#
# # Sets up a persistent stream to ALERT_TOPIC,
# # sends OBS message to save_message_alert()
# def sub_alrt():
#     stream = Stream(persist=True)
#
#     with stream.open(set_topic("A"), "r") as s:
#         for message in s:
#             print(f"saw an ALERT at: {hr_str()} {date_str()} from {message['detector_id']}")
#             save_message_alert(message)
