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
from . import snews_utils
from hop import Stream
import os, json, click
from collections import namedtuple
from .snews_db import Storage
from .snews_coinc import CoincDecider


class HopSubscribe:
    def __init__(self, env_path=None):
        snews_utils.set_env(env_path)
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
        self.storage = Storage(env_path, drop_dbs=True)

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

    # shouldn't verbose always be True?
    def subscribe(self, which_topic='A', verbose=False):
        ''' Subscribe and listen to a given topic
            Arguments
            ---------
            which_topic : str
                Topic to listen. If 'A' or 'O' listens the
                alert or observation topics set by the env file
                long string indicating the full topic link can also
                be given
            verbose : bool
                Whether to display the subscribed message content
                
        '''
        if len(which_topic) == 1:
            # set topic enum, get name and broker
            topic = snews_utils.set_topic_state(which_topic)
            name = topic.topic_name
            broker = topic.topic_broker
            topic_col = 'red' if which_topic.upper() == 'A' else 'blue'
            click.echo('You are subscribing to ' +
                       click.style(f'{name}', bg=topic_col, bold=True) + '\nBroker:' +
                       click.style(f'{broker}', bg='green'))
        else:
            name = which_topic.split('/')[-1]
            broker = which_topic
        # self.logger.info(f'{self.snews_time()}: Listening the {broker}\n')
        # Initiate hop_stream
        stream = Stream(persist=True)
        with stream.open(broker, "r") as s:
            for message in s:
                if which_topic.upper() == 'O':  self.storage.insert_mgs(message)
                if which_topic.upper() == 'A':  snews_utils.display_gif()  # should also insert

                # print(f"\n({name} from {message['detector_name']} at {message['sent_time']})")
                if verbose: publish_format(which_topic, message)
                # Don't need this mgs is already saved on the MongoDB
                # What if the user wants to store the alert messages?
                # Do all users have access to MongoDB? 
                # self.save_message(message)


def publish_format(which_topic, message):
    if which_topic.upper() in ['O', 'H']:
        for k, v in message.items():
            if v == None: v = 'None'
            if k == 'detector_status':
                col = 'red' if v == 'OFF' else 'green' if v == 'ON' else 'blue'
                click.echo(f'# {k:<20s}:' + click.style(f'{str(v):<36}', fg='white', bg=col) + ' #')
            else:
                click.echo(f'# {k:<20s}:{v:<36} #')
        click.echo('#'.center(61, '#'))
    elif which_topic == 'A':
        click.echo(click.style('ALERT MESSAGE'.center(65, '_'), bg='bright_red'))
        for k, v in message.items():
            if type(v) == type(None): v = 'None'
            if type(v) == str:
                click.echo(f'{k:<20s}:{v:<45}')
            elif type(v) == list:
                items = '\t'.join(v)
                if k == 'detector_names':
                    click.echo(f'{k:<20s}' + click.style(f':{items:<45}', bg='blue'))
                else:
                    click.echo(f'{k:<20s}:{items:<45}')
        click.secho('_'.center(65, '_'), bg='bright_red')
