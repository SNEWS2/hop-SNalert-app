# Author: Sebastian Torres-Lara, Univ of Houston

# Imports
import json
import requests

# this method creates a slack request to a test channel (webhook_url)
# Sends either and aler or obs notification (depending on the message state)
def send_slack_msg(topic, message):
    webhook_url = "https://hooks.slack.com/services/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"
    if topic == 'A':
        slack_data = {'text': f"ALERT from: {message['detector_id']}:\n{str(message)}"}
        requests.post(webhook_url, data=json.dumps(slack_data), headers={'Content_type': 'application/json'})
    elif topic == 'O':
        slack_data = {'text': f"OBSERVATION from: {message['detector_id']}:\n{str(message)}"}
        requests.post(webhook_url, data=json.dumps(slack_data), headers={'Content_type': 'application/json'})
