"""
An interface for SNEWS member experiment 
to publish their observation and heartbeat messages.

Created: 
August 2021
Authors: 
Melih Kara
Sebastian Torres-Lara
"""
import hop, sys, time, os, json, click
from hop import Stream
from datetime import datetime
from collections import namedtuple
from dotenv import load_dotenv
from . import snews_utils
from .hop_mgs_schema import Message_Schema
from .snews_db import Storage


# Detector = namedtuple("Detector", ["name", "id", "location"])


class Publish_Heartbeat:
    """ Class to publish heartbeat messages continuously

    Parameters
    ----------
    rate : `int`
        The rate at which the hearbeat messages needs to be published
    env_path : `str`
        path for the environment file.
        Use default settings if not given
    detector : `str`, optional
        The name of the detector. Default is "TEST"

    """

    def __init__(self, rate=30, env_path=None, detector='TEST'):
        self.rate = rate  # seconds
        self.times = snews_utils.TimeStuff(env_path)
        self.heartbeat_topic = os.getenv("OBSERVATION_TOPIC")
        self.detector = detector

    def publish(self):
        """ Publishing method (Uses APScheduler)"""
        self.background_schedule(self.rate)

    def retrieve_status(self):
        """ Place Holder for the detector status
            Needs to be updated to allow for user input in the future.
            Currently randomly returns ON or OFF strings.

        """
        import numpy as np
        return np.random.choice(['ON', 'OFF'])

    def publisher(self):
        """ Publish heartbeat message
            Publish default dict at the given time

        """
        schema = Message_Schema(detector_key=self.detector)
        sent_time = self.times.get_snews_time()
        machine_time = self.times.get_snews_time()
        data = snews_utils.data_obs(detector_status=self.retrieve_status(), machine_time=machine_time)
        heartbeat_message = schema.get_obs_schema(msg_type='Heartbeat', data=data, sent_time=sent_time)

        stream = Stream(persist=True)
        try:
            with stream.open(self.heartbeat_topic, "w") as s:
                s.write(heartbeat_message)
            print(f"\nPublished the Heartbeat message to {self.heartbeat_topic}:")
            for k, v in heartbeat_message.items():
                if k == 'detector_status':
                    col = 'red' if v == 'OFF' else 'green'
                    click.echo(f'{k:<20s}:' + click.style(str(v), fg='white', bg=col))
                else:
                    click.echo(f'{k:<20s}:{v}')
        except:
            print(f'publish() failed at {self.times.get_snews_time()}')

    # NEEDS WORK
    def background_schedule(self, schedule=10):
        """ Publish Heartbeat messages in background
            On a given schedule

            Parameters
            ----------
            schedule : `int`
                The time interval in seconds to publish heartbeat

            Notes
            -----
            Needs more work. Killing the process is not easy.

        """
        from apscheduler.schedulers.background import BackgroundScheduler
        import os

        scheduler = BackgroundScheduler()
        scheduler.add_job(self.publisher, 'interval', seconds=schedule)
        scheduler.start()
        print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
        try:
            # This is here to simulate application activity (which keeps the main thread alive).
            while True:
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            # Not strictly necessary if daemonic mode is enabled but should be done if possible
            scheduler.shutdown()


class Publish_Alert:
    """ Class to publish SNEWS SuperNova Alerts based on coincidence
    
    Notes
    -----
    Only relevant for the server
    """

    def __init__(self, env_path=None, use_local=False):
        snews_utils.set_env(env_path)
        self.broker = os.getenv("HOP_BROKER")
        self.alert_topic = os.getenv("ALERT_TOPIC")
        self.times = snews_utils.TimeStuff(env_path)
        self.time_str = lambda: self.times.get_snews_time()
        self.storage = Storage(drop_db=False, use_local=use_local)

    # decider should call this
    def publish(self, msg_type, data):
        """ Publish alert message
            This function should only be called by the
            CoincDecider class when a coincidence between
            different observations trigger an alert

        Parameters
        ----------
        msg_type : `str`
            Type (Tier) of the message. Has to be one of 
            the 'CoincidenceTierAlert', 'SigTierAlert', 'TimeTierAlert'
        data : `dict`
            Data dictionary received from snews_utils.data_alert()

        """
        schema = Message_Schema(alert=True)
        sent_time = self.times.get_snews_time()
        alert_schema = schema.get_alert_schema(msg_type=msg_type, sent_time=sent_time, data=data)

        stream = Stream(persist=False)
        with stream.open(self.alert_topic, "w") as s:
            s.write(alert_schema)
        self.storage.insert_mgs(alert_schema)
        for k, v in alert_schema.items():
            print(f'{k:<20s}:{v}')

    def publish_retraction(self, retracted_mgs):
        """
        Takes retracted alert and publishes it.

        Parameters
        ----------
        retracted_mgs: 'dict'
            Retracted alert message
        """
        stream = Stream(persist=False)
        with stream.open(self.alert_topic, "w") as s:
            s.write(retracted_mgs)


class Publish_Tier_Obs:
    """ Publish Supernova Observation messages to
        different tiers.
    
    Parameters
    ---------- 
    env_path : `str`
        path for the environment file.
        Use default settings if not given
    
    """

    def __init__(self, env_path=None):
        snews_utils.set_env(env_path)
        self.times = snews_utils.TimeStuff()
        self.obs_broker = os.getenv("OBSERVATION_TOPIC")

    def publish(self, detector, msg_type, data):
        """ Publish message to stream

        Parameters
        ----------
        detector : `str`
            The name of the detector
        msg_type : `str`
            Type (Tier) of the message. Has to be one of 
            the 'CoincidenceTier', 'SigTier', 'TimeTier', 'FalseOBS'
        data : `dict`
            Data dictionary received from snews_utils.data_obs()

        """
        schema = Message_Schema(detector_key=detector)
        sent_time = self.times.get_snews_time()
        obs_schema = schema.get_obs_schema(msg_type, data, sent_time)

        stream = Stream(persist=False)
        with stream.open(self.obs_broker, 'w') as s:
            s.write(obs_schema)
        click.secho(f'{"-" * 57}', fg='bright_blue')
        if mgs_type == 'FalseOBS':
            click.secho("It's okay, we all make mistakes".upper,fg='pink')
        for k, v in obs_schema.items():
            print(f'{k:<20s}:{v}')
