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

def set_topic_state():
    Topics = namedtuple('Topics',['broker','topic_sever','topic_name'])
    topics ={'ALERT'}
"""
hop-subscribe class
"""

class Hop_Subscribe:
    def __init__(self):
        self.hop_broker = "kafka.scimma.org"
        self.observation_topic = f"kafka://{self.hop_broker}/snews.experiments-test"
        self.alert_topic = f"kafka://{self.hop_broker}/snews.alert-test"
        self.hr = snew_util.Time_Stuff.get_hr_str()
        self.date = snew_util.Time_Stuff.get_date_str()
        self.snews_time = snew_util.Time_Stuff.get_snews_time_str()


    def save_mgs(self,detector_name,topic):
        path = f'SNEWS_MSGs/{topic}/{date_str()}/'
        make_dir(path)
        text_file = open(f"{path}SNEWS_OBS_{detector_name}_{hr_str()}.txt", "w+")
        text_file.write(str(message))
        text_file.close()

    def hop_sub(self):



a persistent stream to OBSERVATION_TOPIC,
# sends OBS message to save_message_obs()
# this was a testing method
def sub_obs():
    stream = Stream(persist=True)

    with stream.open(set_topic("O"), "r") as s:
        for message in s:
            print(f"saw an OBS at: {hr_str()} {date_str()} from {message['detector_id']}")
            save_message_obs(message, message['detector_id'])


# Sets up a persistent stream to ALERT_TOPIC,
# sends OBS message to save_message_alert()
def sub_alrt():
    stream = Stream(persist=True)

    with stream.open(set_topic("A"), "r") as s:
        for message in s:
            print(f"saw an ALERT at: {hr_str()} {date_str()} from {message['detector_id']}")
            save_message_alert(message)


