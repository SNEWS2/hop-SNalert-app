"""
An interface for SNEWS member experiment 
to publish their observation and heartbeat messages 

Created: 
August 2021
Authors: 
Melih Kara
Sebastian Torres-Lara
"""
import hop, snews, sys, time, os, json
from hop import Stream
from datetime import datetime
from collections import namedtuple
from dotenv import load_dotenv
import snews_utils
from hop_mgs_schema import Message_Schema

Detector = namedtuple("Detector", ["name", "id", "location"])


class Publish_Heartbeat(Publish):
    """ Class to publish hearbeat messages continuously
    """

    def __init__(self, msg=None, detector='TEST', rate=30, env_path=None):
        super().__init__(msg, detector, env_path)
        self.rate = rate  # seconds
        self.summarize = lambda env_path: snews_utils.summarize(self.detector, "HEARTBEAT", env_path)
        self.run_continouosly = self.background_schedule(self.rate)

    def retrieve_status(self):
        """ Script to retrieve detector status
        """
        import numpy as np
        return np.random.choice(['ON', 'OFF'])

    def publish(self):
        """ Publish heartbeat message
            Publish default dict
        """
        # hb_keys = ['detector_id','sent_time','status']
        # heartbeat_message = {k:v for k,v in self.message_dict if k in hb_keys}
        heartbeat_message = {}
        heartbeat_message['detector_id'] = self.detector.id
        heartbeat_message['message_id'] = self.id_format(topic_type='H')
        heartbeat_message['status'] = self.retrieve_status()
        heartbeat_message['sent_time'] = self.time_str()
        stream = Stream(persist=True)
        try:
            with stream.open(self.heartbeat_topic, "w") as s:
                s.write(heartbeat_message)
            print(f"\nPublished the Heartbeat message to {self.heartbeat_topic}:")
            for k, v in heartbeat_message.items():
                print(f'{k:<20s}:{v}')
        except:
            print(f'publish() failed at {self.time_str()}')

    # NEEDS WORK
    def background_schedule(self, schedule=10):
        """ Publish Heartbeat messages in background
            On a given schedule

            Notes
            -----
            Needs more work. Killing the process is not easy.
        """
        from apscheduler.schedulers.background import BackgroundScheduler
        import os

        scheduler = BackgroundScheduler()
        scheduler.add_job(self.publish, 'interval', seconds=schedule)
        scheduler.start()
        print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
        try:
            # This is here to simulate application activity (which keeps the main thread alive).
            while True:
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            # Not strictly necessary if daemonic mode is enabled but should be done if possible
            scheduler.shutdown()


# Publish Alerts based on coincidince.
# Only relevant for the server
class Publish_Alert:
    """ Class to publish SNEWS SuperNova Alerts
    """

    def __init__(self, env_path=None):
        snews_utils.set_env()
        self.broker = os.getenv("HOP_BROKER")
        self.alert_topic = os.getenv("ALERT_TOPIC")
        self.times = snews_utils.TimeStuff(env_path)
        self.time_str = lambda: self.times.get_snews_time()

    # decider should call this

    def publish(self, type, data_enum):
        schema = Message_Schema()
        sent_time = self.times.get_snews_time()
        alert_schema = schema.get_alert_schema(type, data_enum, sent_time)

        stream = Stream(persist=False)
        with stream.open(self.alert_topic, "w") as s:
            s.write(alert_schema.mgs)
        # print(f"\nPublished ALERT message to {self.alert_topic} !!!")


class Publish_Tier_Obs:
    def __init__(self, env_path=None):
        snews_utils.set_env(env_path)
        self.times = snews_utils.TimeStuff()
        self.obs_broker = os.getenv("OBSERVATION_TOPIC")

    def publish(self, type, data_enum):
        schema = Message_Schema()
        sent_time = self.times.get_snews_time()
        obs_schema = schema.get_obs_schema(type, data_enum, sent_time)

        stream = Stream(persist=False)
        with stream.open(self.obs_broker, 'w') as s:
            s.write(obs_schema.mgs)
            print(obs_schema.mgs)
