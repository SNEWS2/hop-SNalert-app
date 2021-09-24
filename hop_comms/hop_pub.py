"""
An interface for SNEWS member experiment 
to publish their observation and heartbeat messages.

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
from snews_db import Storage
# Detector = namedtuple("Detector", ["name", "id", "location"])


class Publish_Heartbeat:
    """ Class to publish heartbeat messages continuously
    """

    def __init__(self, msg=None, rate=30, env_path=None):
        super().__init__(msg, detector, env_path)
        self.rate = rate  # seconds
        # self.summarize = lambda env_path: snews_utils.summarize(self.detector, "HEARTBEAT", env_path)
        self.run_continuously = self.background_schedule(self.rate)

    def retrieve_status(self):
        """ Script to retrieve detector status
        """
        import numpy as np
        return np.random.choice(['ON', 'OFF'])

    def publish(self,detector='TEST'):
        """ Publish heartbeat message
            Publish default dict
        """
        # hb_keys = ['detector_id','sent_time','status']
        # heartbeat_message = {k:v for k,v in self.message_dict if k in hb_keys}
        schema = Message_Schema(detector_key=detector)
        sent_time = self.time_str()
        machine_time = self.time_str()
        data_enum = snews_utils.data_enum_obs(detector_status=self.retrieve_status(), machine_time=machine_time)
        heartbeat_message = schema.get_schema(msg_type='Heartbeat', data_enum=data_enum, sent_time=sent_time)

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


# Publish Alerts based on coincidence.
# Only relevant for the server
class Publish_Alert:
    """ Class to publish SNEWS SuperNova Alerts
    """

    def __init__(self, env_path=None):
        snews_utils.set_env(env_path)
        self.broker = os.getenv("HOP_BROKER")
        self.alert_topic = os.getenv("ALERT_TOPIC")
        self.times = snews_utils.TimeStuff(env_path)
        self.time_str = lambda: self.times.get_snews_time()
        self.storage = Storage(drop_dbs=False)

    # decider should call this
    def publish(self, msg_type, data_enum):
        schema = Message_Schema(alert=True)
        sent_time = self.times.get_snews_time()
        alert_schema = schema.get_alert_schema(msg_type=msg_type, sent_time=sent_time, data_enum=data_enum)

        stream = Stream(persist=False)
        with stream.open(self.alert_topic, "w") as s:
            s.write(alert_schema.mgs)
        alert_type = alert_schema.mgs['_id'].split('_')[0]
        self.storage.insert_mgs(mgs)
        # print(f"\nPublished ALERT message to {self.alert_topic} !!!")


class Publish_Tier_Obs:
    def __init__(self, env_path=None):
        snews_utils.set_env(env_path)
        self.times = snews_utils.TimeStuff()
        self.obs_broker = os.getenv("OBSERVATION_TOPIC")

    def publish(self, detector, msg_type, data_enum):
        schema = Message_Schema(detector_key=detector)
        sent_time = self.times.get_snews_time()
        obs_schema = schema.get_obs_schema(msg_type, data_enum, sent_time)

        stream = Stream(persist=False)
        with stream.open(self.obs_broker, 'w') as s:
            s.write(obs_schema.mgs)
            print(obs_schema.mgs)