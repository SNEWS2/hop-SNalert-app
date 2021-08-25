import sys
import hop
from hop import Stream
from datetime import datetime
import time
import snews


class Publish:
    """ Class to format and publish messages
    """
    def __init__(self, message=dict()):
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
        self.heartbeat_topic   = f"kafka://{self.broker}/snews.alert-test"
        self.__version__ = "0.0.2"


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
                "detector_id": 0, 
                "sent_time": "01/01/01 01:01:01", 
                "neutrino_time": "01/01/01 01:01:01", 
                "machine_time": "01/01/01 01:01:01", 
                "location": "none", 
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


    def publish_to_tiers(self):
        """ Publish messages to the indicated streams
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


class Publish_Observation(Publish):
    """ Class to publish observation messages

    """
    def __init__(self, msg=dict(), welcome=False):
        super().__init__(msg)
        if welcome: self.summarize()
        
    def summarize(self):
        """ Summarize the current configuration
        """
        header = f'\n### Publish SNEWS Observation Messages ###\n'
        versions = f'Your Python version:{sys.version}\n'+\
        f'Current hop-client version:{hop.__version__}\n'+\
        f'             snews version:{snews.__version__}\n\n'
        topic_info = f'Publishing to {self.broker}\n'+\
        f' Observation Topic: {self.alert_topic}\n\n'
        tier_info = f'Submitting messages to the following Tiers;\n'+\
        f'{" & ".join([tier for tier in self.publish_to.keys() if self.publish_to[tier]==True])}\n'
        f'See self.publish_to to change\n'
        print(header,versions,topic_info, tier_info)
    
    
class Publish_Heartbeat(Publish):
    """ Class to publish hearbeat messages continuously
    
    """
    def __init__(self, msg):
        super().__init__(self, msg)