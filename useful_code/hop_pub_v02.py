import hop, snews, sys, time, os, json
from hop import Stream
from datetime import datetime
from enum import Enum
from collections import namedtuple
from dotenv import load_dotenv
import uuid
  
   
Detector = namedtuple("Detector", ["name", "id", "location"])

class Publish:
    """ Class to format and publish messages
    """
    def __init__(self, message, detector, env_path):
        self.detectors = self.retrieve_detectors()
        self.detector = self.get_detector(detector)
        self.publish_to = {'Significance_Tier':True, 'Coincidence_Tier':True, 'Timing_Tier':True}        
        self.common_keys_ = ['detector_id','machine_time','neutrino_time','status']
        self.tier_keys_   = {'Significance_Tier':self.common_keys_ + ['p_value'],
                             'Coincidence_Tier':self.common_keys_,
                             'Timing_Tier':self.common_keys_ + ['time-series']}
        self.set_env(env_path)
        self.broker            = os.getenv("HOP_BROKER")
        self.observation_topic = os.getenv("OBSERVATION_TOPIC")
        self.alert_topic       = os.getenv("ALERT_TOPIC")
        self.heartbeat_topic   = self.observation_topic 
        self.time_str_format   = os.getenv("TIME_STRING_FORMAT")
        self.message_dict = message
        self.format_message(message)
        self.__version__ = "0.0.4"


    def set_env(self, env_path=None):
        """ Set environment
        Arguments
        ---------
        env_path : str (optional)
            path for the environment file. 
            Use default settings if not given
        """
        env = env_path or './default_env.env'
        load_dotenv(env)

            
    def time_str(self):
        """ Returns datetime object for current time 
            year/month/day hr:min:sec (UTC)
        """
        return datetime.now().utcnow().strftime(self.time_str_format)
    

    # retrieve the detector properties
    def retrieve_detectors(self):
        if not os.path.isfile('detector_properties.json'):
            os.system('python make_detector_file.py')

        with open('detector_properties.json') as json_file:
            detectors = json.load(json_file)

        for k,v in detectors.items():
            detectors[k] = Detector(v[0], v[1], v[2])
        return detectors

    
    def get_detector(self, detector):
        """ Return the selected detector properties
        """
        if isinstance(detector, Detector): return detector
        if isinstance(detector, str): 
            try:
                return self.detectors[detector]
            except KeyError:
                print(f'{detector} is not a valid detector!')
                return self.detectors['TEST']


    def default_dict(self):
        """ Returns the default dictionary
            with all entries being 'none'
        """
        return {"message_id": str(uuid.uuid4()), 
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
        if isinstance(message,str):
            pass


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
        print(f"\n> modify self.message_dict or \n> use .publish_to_tiers() method to publish (see .publish_to)")


class Publish_Observation(Publish):
    """ Class to publish observation messages
    """
    def __init__(self, msg=None, detector='TEST', welcome=False, env_path=None):
        super().__init__(msg, detector, env_path)
        if welcome: self.summarize()
        
    def summarize(self):
        """ Summarize the current configuration
        """
        print(
        '#'.ljust(50, '#')+
        f'\n# {"Publish SNEWS Observation Messages":^46} #\n'
        f'#{self.detector.name:_^48}#\n'
        f'#{str(self.detector.id)+"-"+self.detector.location:_^48}#\n'+
        '#'.center(51, '#')+
        f'\nYour Python version:\n {sys.version}\n'
        f'Current hop-client version:{hop.__version__}\n'
        f'             snews version:{snews.__version__}\n\n'
        f'Publishing to {self.broker}\n'
        f'Observation Topic:\n==> {self.observation_topic}\n\n'
        f'> Selected Tiers;\n'
        f'{" & ".join([tier for tier in self.publish_to.keys() if self.publish_to[tier]==True])}\n'
        '-> to change, modify `self.publish_to`')
    
    
    def publish(self):
        """ Publish the current message
        """
        self.message_dict['status'] = 'ON'
        stream = Stream(persist=False)
        with stream.open(self.observation_topic, "w") as s:
            s.write(self.message_dict)
        print(f"\nPublished OBS message to {self.observation_topic}:")
        for k,v in self.message_dict.items():
            print(f'{k:<20s}:{v}')
    
    
class Publish_Heartbeat(Publish):
    """ Class to publish hearbeat messages continuously
    """
    def __init__(self, msg=None, detector='TEST', rate=30, env_path=None):
        super().__init__(msg, detector, env_path)
        self.rate = rate     # seconds          
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