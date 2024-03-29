# Author: Sebastian Torres-Lara, Univ of Houston

# Imports
from datetime import datetime
from hop import Stream
from pathlib import Path
import os
import slack_alert


# get current time
def hr_str():
    return datetime.now().utcnow().strftime("%H:%M:%S")


# get current date
def date_str():
    return datetime.now().utcnow().strftime("%y_%m_%d")


# make dir with current data (yr_m_d)
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


# Sets up a persistent stream to OBSERVATION_TOPIC,
# sends OBS message to save_message_obs()
def sub_obs():
    stream = Stream(persist=True)

    with stream.open(set_topic("O"), "r") as s:
        for message in s:
            # print(f"saw an OBS at: {time_str()} from {message['detector_id']}")
            slack_alert.send_slack_msg('O', message)
            save_message_obs(message, message['detector_id'])


# Sets up a persistent stream to ALERT_TOPIC,
# sends OBS message to save_message_alert()
def sub_alrt():
    stream = Stream(persist=True)

    with stream.open(set_topic("A"), "r") as s:
        for message in s:
            # print(f"saw an ALERT at: {time_str()} from {message['detector_id']}")
            slack_alert.send_slack_msg('A', message)
            save_message_alert(message)


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

# Whenever an alert is sent this method will search throug
def alert_send_rev_search():
    pass
#     with stream.open(set_topic("A"), "r") as s:
#         for message in s:
#         # send to reverse search module
