from collections import namedtuple
from . import snews_utils
from .snews_utils import TimeStuff
import sys

class Message_Schema:
    """ The Message scheme for the alert and observations

    Parameters
    ----------
    env_path : `str`, optional
        The path containing the environment configuration file
        If None, uses the default file in '/auxiliary/test-config.env'
    detector_key : `str`, optional
        The name of the detector. If None, uses "TEST"
    alert : `bool`, optional
        True if the message is ALERT message. Default is False.

    """

    def __init__(self, env_path=None, detector_key='TEST', alert=False):
        if alert:
            self.times = TimeStuff(env_path)
        else:
            self.detector = snews_utils.get_detector(detector_key)
            self.detector_name = self.detector.name
            self.detector_loc = self.detector.location
            self.times = TimeStuff(env_path)

    def id_format(self, topic_state, topic_type):
        """ Returns formatted message ID
            time format should always be same for all detectors.
            The heartbeats and observation messages have the 
            same id format.

        Parameters
        ----------
        topic_state : `str`
            Can either be 'OBS', or  'ALERT'
        topic_type : `str`
            type of the message to be published. Can be;
            'TimeTier', 'SigTier', 'CoincidenceTier' for
            observation messages and, 'HeartBeat' for 
            heartbeat messages, and 'FalseOBS' for false
            observations.

        Returns
            :`str`
                The formatted id as a string
            
        """
        date_time = self.times.get_snews_time(fmt="%y/%m/%d_%H:%M:%S:%f")
        if topic_state == 'OBS':
            return f'{self.detector.id}_{topic_type}_{date_time}'
        elif topic_state == 'ALERT':
            return f'SNEWS_{topic_type}_{date_time}'
        else:
            sys.exit(f'{topic_state} is not valid!\nOptions are ["OBS","ALERT","FalseOBS"]')

    def get_obs_schema(self, msg_type, data, sent_time):
        """ Create a message schema for given topic type.
            Internally called in hop_pub

            Parameters
            ----------
            msg_type : `str`
                type of the message to be published. Can be;
                'TimeTier', 'SigTier', 'CoincidenceTier' for
                observation messages and, 'HeartBeat' for 
                heartbeat messages
            data      : `named tuple`
                snews_utils data tuple with predefined field.
            sent_time : `str`
                time as a string
            
            Returns
            -------
               :`dict`
                message with the correct scheme 

        """
        base = {"_id": self.id_format("OBS", f'{msg_type}'),
                "detector_name": self.detector_name,
                "sent_time": sent_time,
                "machine_time": data['machine_time'],
                "location": self.detector_loc,
                "detector_status": data['detector_status']}

        messages = {}
        messages['Heartbeat'] = base.copy()

        messages['TimeTier'] = base.copy()
        messages['TimeTier']['neutrino_time'] = data['neutrino_time']
        messages['TimeTier']['timing_series'] = data['timing_series']

        messages['SigTier'] = base.copy()
        messages['SigTier']['neutrino_time'] = data['neutrino_time']
        messages['SigTier']['p_value'] = data['p_value']

        messages['CoincidenceTier'] = base.copy()
        messages['CoincidenceTier']['neutrino_time'] = data['neutrino_time']
        messages['CoincidenceTier']['p_value'] = data['p_value']

        look_for = 0
        N_look_for = 0
        if data['look_for_latest'] == 1:
            look_for = 1
        if data['N_look_for_latest'] > 0 :
            N_look_for = data['N_look_for_latest']

        messages['FalseOBS'] = {'_id': self.id_format("OBS", "FalseOBS"),
                                'detector_name': self.detector_name,
                                'false_id': data['false_id'],
                                'look_for_latest': look_for,
                                'N_look_for_latest': N_look_for,
                                'sent_time': sent_time}

        message = messages[msg_type]
        # check if data contains unknown (extra) fields
        known_keys = [[k for k in messages[tier].keys()] for tier in messages.keys()]
        known_keys = [item for sublist in known_keys for item in sublist]
        # extra_keys = [key for key in data.keys() if key not in message.keys()]
        extra_keys = [key for key in data.keys() if key not in known_keys]
        if len(extra_keys) > 0:
            for key in extra_keys:
                if key == 'false_id' and msg_type != 'FalseOBS': continue
                message['^' + key] = data[key]
        return message

    def get_alert_schema(self, msg_type, sent_time, data):
        """ Create a message schema for given topic type.
            Internally called in hop_pub
        
            Parameters
            ----------
            msg_type : `str`
                type of the message to be published. Can be;
                'TimeTier', 'SigTier', 'CoincidenceTier' for
                observation messages and, 'HeartBeat' for 
                heartbeat messages
            data : `named tuple`
                snews_utils data tuple with predefined field.
            sent_time : `str`
                time as a string
            
            Returns
            -------
                :`dict`
                    message with the correct scheme 

        """
        base = {"_id": self.id_format("ALERT", f'{msg_type}'),
                "detector_names": data['detectors'],
                "ids": data['ids'],
                "sent_time": sent_time,
                "neutrino_times": data['neutrino_times'],
                "machine_times": data['machine_times'],
                # "locations": data['locs']
                }

        messages = {}
        messages['CoincidenceTierAlert'] = base.copy()
        messages['SigTierAlert'] = base.copy()
        messages['TimeTierAlert'] = base.copy()
        messages['TimeTierAlert']['timing_series'] = data['t_series']
        return messages[msg_type]

### comment from Melih:
### get_alert_schema is almost the same as the get_obs_schema
### the only difference comes in when formatting the ID. 
### Since both these functions are backhand, we can easily merge them
###-----------
### Moreover, why do the ALERT messages have detector ids or status?
