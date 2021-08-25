import hop, snews, sys
from hop import Stream
from datetime import datetime
import time
import snews
from enum import Enum

exp_locations = {1:'loc SuperK',2:'loc HyperK', 3:'loc SNO+', 4:'loc KamLAND',
                 5:'loc LVD', 6:'loc ICECUBE', 7:'loc Borexino', 8:'loc HALO_1kT', 
                 9:'loc HALO', 10:'loc NOvA', 11:'loc KM3NeT', 12:'loc Baksan', 13:'loc JUNO', 
                 14:'loc LZ', 15:'loc DUNE', 16:'loc MicroBooNe', 17:'loc SBND', 18:'loc DS_20k', 
                 19:'loc XENONnT', 20:'loc PandaX_4t'}

class Experiment(Enum):
    """ Enumerated Experiments

        Notes:
        print(Experiment.KamLAND.name)
        > KamLAND
        print(Experiment.KamLAND.value)
        > 4
    """

    Super_K, SuperK   = 1, 1
    Hyper_K, HyperK   = 2, 2
    SNOp,SNOplus      = 3, 3
    KamLAND   = 4
    LVD       = 5
    ICE, IceCube      = 6, 6
    Borexino  = 7
    HALO_1kT, HALO1kT  = 8, 8
    HALO      = 9
    NOvA      = 10
    KM3NeT    = 11
    Baksan    = 12
    JUNO      = 13
    LZ        = 14
    DUNE      = 15
    MicroBooNe= 16
    SBND      = 17
    DS_20K, DS20K    = 18, 18
    XENONnT   = 19
    PandaX_4T, PandaX4T = 20, 20

class Publish:
    """ Class to format and publish messages
    """
    def __init__(self, message=dict(), experiment=None):
        self.set_experiment_properties_(experiment)
        self.publish_to = {'Significance_Tier':True, 'Coincidence_Tier':True, 'Timing_Tier':True}
        self.msg_dict   = self.default_dict()
        self.format_message_(message)
        
        self.common_keys_ = ['detector_id','machine_time','neutrino_time','status']
        self.tier_keys_   = {'Significance_Tier':self.common_keys_ + ['p_value'],
                             'Coincidence_Tier':self.common_keys_,
                             'Timing_Tier':self.common_keys_ + ['time-series']}
        self.broker            = "kafka.scimma.org"
        self.observation_topic = f"kafka://{self.broker}/snews.experiments-test"
        self.alert_topic       = f"kafka://{self.broker}/snews.alert-test"
        self.heartbeat_topic   = f"kafka://{self.broker}/snews.testing" # should the HB pub to alert?
        self.__version__ = "0.0.3"

        
    def set_experiment_properties_(self, experiment):
        """ Sets the experiment-specific properties
        """
        if type(experiment)==type(None):
            self.exp_name = 'Not Specified'
            self.exp_id = -999
            self.exp_loc = 'Not Specified'
        else:
            self.exp_name = experiment.name
            self.exp_id   = experiment.value
            self.exp_loc  = exp_locations[self.exp_id]

            
    def time_str(self):
        """ Returns datetime object for current time 
            year/month/day hr:min:sec (UTC)
        """
        return datetime.now().utcnow().strftime("%y/%m/%d %H:%M:%S")


    def default_dict(self):
        """ Returns the default dictionary
            with all entries being 'none'
        """
        return {"message_id": 0, 
                "detector_id": self.exp_id, 
                "sent_time": self.time_str(), 
                "neutrino_time": "01/01/01 01:01:01", 
                "machine_time": "01/01/01 01:01:01", 
                "location": self.exp_loc, 
                "p_value": 0, 
                "status": "none", 
                "content": "none",
                "time-series":0}


    def format_message_(self, message):
        """ Format the message
        """
        if isinstance(message,dict):
            # overwrite default ones, add new ones, keep missing ones
            self.msg_dict = {**self.msg_dict, **message}
        if isinstance(message,list):
            pass


    def publish_to_tiers(self):                             # TODO: check tiers, combine keys
        """ Publish messages to the indicated streams       # Submit one message containing all
        """
        for tier, flag in self.publish_to.items():
            if flag:
                # if publish_to:tier is True
                # select the relevant keys
                tier_data = {x:self.msg_dict[x] for x in self.tier_keys_[tier]}
                stream = Stream(persist=False)
                with stream.open(self.observation_topic, "w") as s:
                    s.write(tier_data)
                print(f"\nPublishing OBS message to {tier}:")
                for k,v in tier_data.items():
                      print(f'{k:<20s}:{v}')
                        
                    
    def display_message(self):
        """ Display the mesagge without publishing
        """
        print(f"Following OBS message to be published:\n{self.time_str()}\n")
        for k,v in self.msg_dict.items():
              print(f'{k:<20s}:{v}')
        print(f"\n> modify self.msg_dict or \n> use .publish_to_tiers() method to publish (see .publish_to)")


class Publish_Observation(Publish):
    """ Class to publish observation messages
    """
    def __init__(self, msg=dict(), experiment=None, welcome=False):
        super().__init__(msg, experiment=experiment)
        if welcome: self.summarize()
        
    def summarize(self):
        """ Summarize the current configuration
        """
        header = f'\n ### Publish SNEWS Observation Messages ###\n'
        exp_str = ''
        if self.exp_id != -999: exp_str=f'#{self.exp_name:_^40}#\n'
        versions = f'Your Python version:{sys.version}\n'+\
        f'Current hop-client version:{hop.__version__}\n'+\
        f'             snews version:{snews.__version__}\n\n'
        topic_info = f'Publishing to {self.broker}\n'+\
        f' Observation Topic: {self.observation_topic}\n\n'
        tier_info = f'> Submitting messages to the following Tiers;\n'+\
        f'{" & ".join([tier for tier in self.publish_to.keys() if self.publish_to[tier]==True])}\n'
        f'See self.publish_to to change\n'
        print(header,exp_str,versions,topic_info, tier_info)
    
    
    def publish(self):
        """ Publish the current message
        """
        stream = Stream(persist=False)
        with stream.open(self.observation_topic, "w") as s:
            s.write(self.msg_dict)
        print(f"\nPublished OBS message to {self.observation_topic}:")
        for k,v in self.msg_dict.items():
            print(f'{k:<20s}:{v}')
    
    
class Publish_Heartbeat(Publish):
    """ Class to publish hearbeat messages continuously
    """
    def __init__(self, msg=dict(), experiment=None,):
        super().__init__(msg, experiment)
        self.rate = 60     # seconds            
     
    def retrieve_status(self):
        """ Script to retrieve detector status
        """
        import numpy as np
        return np.random.choice(['ON','OFF'])
    
    # TODO: needs to run continously in background
    # until stopped
    def publish(self):
        """ Publish the current message
        """
        heartbeat_message = self.msg_dict
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
    def background_schedule(self):
        from apscheduler.schedulers.background import BackgroundScheduler
        import os 

        def tick():
            print('Tick! The time is: %s' % datetime.now())

        scheduler = BackgroundScheduler()
#         scheduler.add_job(tick, 'interval', seconds=30)
        scheduler.add_job(self.publish, 'interval', seconds=10)
        scheduler.start()
        print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
        try:
            # This is here to simulate application activity (which keeps the main thread alive).
            while True:
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            # Not strictly necessary if daemonic mode is enabled but should be done if possible
            scheduler.shutdown()