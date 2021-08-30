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
  
Detector = namedtuple("Detector", ["name", "id", "location"])

class Publish:
    """ Class to format and publish messages
    """
    def __init__(self, message, detector, env_path):
        ####
        self.publish_to = {'Significance_Tier':True, 'Coincidence_Tier':True, 'Timing_Tier':True}        
        self.common_keys_ = ['detector_id','machine_time','neutrino_time','status']
        self.tier_keys_   = {'Significance_Tier':self.common_keys_ + ['p_value'],
                             'Coincidence_Tier':self.common_keys_,
                             'Timing_Tier':self.common_keys_ + ['time-series']}
        ####
        self.detector = snews_utils.get_detector(detector)
        snews_utils.set_env(env_path)
        self.broker            = os.getenv("HOP_BROKER")
        self.observation_topic = os.getenv("OBSERVATION_TOPIC")
        self.alert_topic       = os.getenv("ALERT_TOPIC")
        self.heartbeat_topic   = self.observation_topic 
        self.times = snews_utils.TimeStuff(env_path)
        self.time_str = lambda : self.times.get_snews_time()

        self.message_dict = message
        self.format_message(message)
        self.__version__ = "0.0.5"


    def id_format(self, topic_type='O'):
        """ Returns formatted message ID
            time format should always be same for all detectors
        """
        date_time = self.times.get_snews_time(fmt="%y/%m/%d_%H:%M:%S")
        return f'{self.detector.id}_{topic_type}_{date_time}'


    def default_dict(self):
        """ Returns the default dictionary
            with all entries being 'none'
        """
        return {"message_id": self.id_format(), 
                "detector_id": self.detector.id, 
                "sent_time": self.time_str(), 
                "neutrino_time": self.time_str(), 
                "machine_time": self.time_str(), 
                "location": self.detector.location, 
                "p_value": 0, 
                "status": "none", 
                "content": "none"}


    def format_message(self, message):
        """ Format the message
            Takes the deafult dict and modifies the fields
            according to input message
        """
        # if no message is provided, make default
        if type(message)==type(None):
            self.message_dict = self.default_dict()
        if isinstance(message,dict):
            # overwrite default ones, add new ones, keep missing ones
            self.message_dict = {**self.message_dict, **message}
        if isinstance(message,list):
            pass
        if isinstance(message,hop.plugins.snews.SNEWSObservation):
            pass
        # read from a file
        if isinstance(message,str):
            try:
                with open(message) as json_file:
                    self.message_dict = json.load(json_file)
            except:
                print(f'{message} is not a json file!'
                    'Using a default example dict')
                self.message_dict = self.default_dict()
            finally:
                self.format_message(self.message_dict)


    # How to handle different tiers?
    # Currently it publishes one message for each tier
    # masks the unrelevant fields for each
    def publish_to_tiers(self):                             # TODO: check tiers, combine keys
        """ Publish messages to the indicated streams       # Submit one message containing all
        """
        for tier, flag in self.publish_to.items():
            if flag:
                # if publish_to:tier is True
                # select the relevant keys
                tier_data = {x:self.message_dict[x] for x in self.tier_keys_[tier]}
                stream = Stream(persist=False)
                with stream.open(self.observation_topic, "w") as s:
                    s.write(tier_data)
                print(f"\nPublishing OBS message to {tier}:")
                for k,v in tier_data.items():
                      print(f'{k:<20s}:{v}')
                        
                    
    def display_message(self):
        """ Display the mesagge without publishing
        """
        print(f"Following OBS message to be published:\nCurrent time:{self.time_str()}\n")
        for k,v in self.message_dict.items():
              print(f'{k:<20s}:{v}')
        print(f"\n> modify self.message_dict or \n"
               "> use .publish_to_tiers() method to publish (see .publish_to)")


class Publish_Observation(Publish):
    """ Class to publish observation messages
    """
    def __init__(self, msg=None, detector='TEST', welcome=False, env_path=None):
        super().__init__(msg, detector, env_path)
        self.summarize = lambda env_path : snews_utils.summarize(self.detector, "OBSERVATION", env_path)
        if welcome: self.summarize(env_path)

    
    def publish(self):
        """ Publish the current message
        """
        obs_message = self.message_dict
        obs_message['message_id'] = self.id_format(topic_type='O')
        obs_message['status'] = 'ON'
        stream = Stream(persist=False)
        with stream.open(self.observation_topic, "w") as s:
            s.write(obs_message)
        print(f"\nPublished OBS message to {self.observation_topic}:")
        for k,v in obs_message.items():
            print(f'{k:<20s}:{v}')
    
    
class Publish_Heartbeat(Publish):
    """ Class to publish hearbeat messages continuously
    """
    def __init__(self, msg=None, detector='TEST', rate=30, env_path=None):
        super().__init__(msg, detector, env_path)
        self.rate = rate     # seconds          
        self.summarize = lambda env_path : snews_utils.summarize(self.detector, "HEARTBEAT", env_path)
        self.run_continouosly = self.background_schedule(self.rate)
     

    def retrieve_status(self):
        """ Script to retrieve detector status
        """
        import numpy as np
        return np.random.choice(['ON','OFF'])
    

    def publish(self):
        """ Publish heartbeat message
            Publish default dict
        """
        heartbeat_message = self.message_dict
        heartbeat_message['message_id'] = self.id_format(topic_type='H')
        heartbeat_message['status'] = self.retrieve_status()
        heartbeat_message['sent_time'] = self.time_str()
        stream = Stream(persist=True)
        try:
            with stream.open(self.observation_topic, "w") as s:
                s.write(heartbeat_message)
            print(f"\nPublished the Heartbeat message to {self.observation_topic}:")
            for k,v in heartbeat_message.items():
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
        snews_utils.set_env(env_path)
        self.broker            = os.getenv("HOP_BROKER")
        self.alert_topic       = os.getenv("ALERT_TOPIC")
        self.times = snews_utils.TimeStuff(env_path)
        self.time_str = lambda : self.times.get_snews_time()

    # decider should call this
    def publish():
        from IPython.display import HTML, display
        giphy_snews = "https://raw.githubusercontent.com/SNEWS2/hop-SNalert-app/KaraMelih-dev/useful_code/snalert.gif"
        if snews_utils.isnotebook():
            display(HTML(f'<img src={giphy_snews}>'))
        
