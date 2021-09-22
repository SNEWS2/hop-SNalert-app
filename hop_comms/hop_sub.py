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
import os, json
from collections import namedtuple
from snews_db import Storage


class HopSubscribe:
    def __init__(self, env_path=None):
        snews_utils.set_env()
        self.broker = os.getenv("HOP_BROKER")
        self.observation_topic = os.getenv("OBSERVATION_TOPIC")  # only snews can subscribe
        self.alert_topic = os.getenv("ALERT_TOPIC")
        # for testing
        self.heartbeat_topic = self.observation_topic
        self.logger = snews_utils.get_logger('snews_sub', 'logging.log')

        # time object/strings
        self.times = snews_utils.TimeStuff(env_path)
        self.hr = self.times.get_hour()
        self.date = self.times.get_date()
        self.snews_time = lambda: self.times.get_snews_time()
        self.storage = Storage(env_path)
    # don't need this
    def save_message(self, message):
        """ Save messages to a json file
        """
        path = f'SNEWS_MSGs/{self.times.get_date()}/'
        snews_utils.make_dir(path)
        file = path + 'subscribed_messages.json'
        # read the existing file
        try:
            data = json.load(open(file))
            if not isinstance(data, dict):
                print('Incompatible file format!')
                return None
            # TODO: deal with `list` type objects
        except:
            data = {}
        # add new message with a current time stamp
        current_time = self.snews_time()
        data[current_time] = message
        with open(file, 'w') as outfile:
            json.dump(data, outfile, indent=4, sort_keys=True)
        # self.logger.info(str(message))

    def subscribe(self, which_topic='A', verbose=False):
        ''' Subscribe and listen to a given topic
            Arguments
            ---------
            which_topic : str
                Topic to listen. If 'A' or 'O' listens the
                alert or observation topics set by the env file
                long string indicating the full topic link can also
                be given

        '''
        if len(which_topic) == 1:
            # set topic enum, get name and broker
            topic = snews_utils.set_topic_state(which_topic)
            name = topic.topic_name
            broker = topic.topic_broker
            print(f'Subscribing to {name} Topic\nBroker:{broker}')
        else:
            name = which_topic.split('/')[-1]
            broker = which_topic
        # self.logger.info(f'{self.snews_time()}: Listening the {broker}\n')
        # Initiate hop_stream
        stream = Stream(persist=True)
        with stream.open(broker, "r") as s:
            for message in s:
                self.storage.insert_mgs(message)
                print(message)

                if which_topic.upper() == 'A':
                    snews_utils.display_gif()
                else:
                    print(f"{name} from {message['_id']}"
                          f" at {message['sent_time']}")
                if verbose:
                    print('#'.center(50, '#'))
                    for k, v in message.items():
                        print(f'# {k:<20s}:{v:<25} #')
                    print('#'.center(50, '#'))
                # Don't need this mgs is already saved on the MongoDB
                # self.save_message(message)

                # print(message)
