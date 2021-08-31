# Author: Sebastian Torres-Lara, Univ of Houston
# imports
from slack_sdk import WebClient


# from slack_sdk.errors import SlackApiError

#  make sure you have the slackAPI installed pip install slack_sdk

# this method makes the snews msgs easier to read
def readable_msgs(dic):
    msg = ''
    for key in dic:
        msg += f'{key} --> {dic[key]} \n'
    return msg


# this method send a slack message to SNEWS_ALERTS-general
def send_slack_msg(message_type, snews_message):
    # verification token for slack app and channel id
    slack_token = 'xoxb-2120915545714-2134186008769-efonv0EKfryvAH7JNde6IrMm'
    slack_channel_id = 'C02344AHKHV'
    # set up client and give it the slack token
    client = WebClient(token=slack_token)
    # format message
    slack_message = f"Message from {snews_message['detector_id']}\nType: {message_type}\n{readable_msgs(snews_message)}\n\n"
    # pass message to WebClient and send it to the slack channel
    client.chat_postMessage(channel=slack_channel_id, text=slack_message)
