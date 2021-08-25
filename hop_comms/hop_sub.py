# Author: Sebastian Torres-Lara, Univ of Houston

# Imports
from datetime import datetime
from hop import Stream
from pathlib import Path
import os


# get current time (hr:min:sec)
def hr_str():
    return datetime.utcnow().strftime("%H:%M:%S")


# get current date (yr_month_day)
def date_str():
    return datetime.utcnow().strftime("%y_%m_%d")


# make dir with current date
def make_dir(path):
    if Path(path).is_dir():
        pass
    else:
        os.makedirs(path)


# this method sets up the source for the Stream
def set_topic(topic_type):
    hop_broker = "kafka.scimma.org"
    observation_topic = f"kafka://{hop_broker}/snews.experiments-test"
    alert_topic = f"kafka://{hop_broker}/snews.alert-test"

    if topic_type == "A":
        return alert_topic
    elif topic_type == "O":
        return observation_topic
    else:
        print(
            "INVALID ENTRY:\nUse 'A' for ALERT_TOPIC \nOR\n 'O' for OBSERVATION_TOPIC"
        )


# This method converts hop OBS messages to a string and saves it to a txt file
def save_message_obs(message, detector_name):
    path = f'SNEWS_MSGs/OBS/{date_str()}/'
    make_dir(path)
    text_file = open(f"{path}SNEWS_OBS_{detector_name}_{hr_str()}.txt", "w+")
    text_file.write(str(message))
    text_file.close()


# This method converts hop ALERT messages to a string and saves it to a txt file
def save_message_alert(message):
    path = f'SNEWS_MSGs/ALERT/{date_str()}/'
    make_dir(path)
    text_file = open(f"{path}SNEWS_ALERT_{hr_str()}.txt", "w+")
    text_file.write(str(message))
    text_file.close()


# Sets up a persistent stream to OBSERVATION_TOPIC,
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


# Whenever an alert is sent this method will search throug
def alert_send_rev_search():
    pass
#     with stream.open(set_topic("A"), "r") as s:
#         for message in s:
#         # send to reverse search module
