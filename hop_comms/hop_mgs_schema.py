import snews_utils
from collections import namedtuple
from snews_utils import TimeStuff


class Message_Schema:
    def __init__(self, env_path=None, detector_key='Detector0',alert = False):
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
        """
        date_time = self.times.get_snews_time(fmt="%y/%m/%d_%H:%M:%S")
        if topic_state == 'OBS':
            return f'{self.detector.id}_{topic_type}_{date_time}'
        elif topic_state == 'ALERT':
            return f'SNEWS_{topic_type}_{date_time}'

    def get_obs_schema(self, msg_type, data_enum, sent_time):
        """ Create a message schema for given topic type.
            Internally called in hop_pub
            Arguments
            ---------
            msg_type : str
                type of the message to be published. Can be;
                'TimeTier', 'SigTier', 'CoincidenceTier' for
                observation messages and, 'HeartBeat' for 
                heartbeat messages
            data_enum : named tuple
                snews_utils data tuple with predefined field.
            sent_time : str
                time as a string
            
            Returns
            -------
                dict, message with the correct scheme 

        """
        message_type = namedtuple('message_type', ['topic_name', 'mgs'])
        messages = {
            "TimeTier": message_type('TimeTier', {
                "_id": self.id_format("OBS", "TimeTier"),
                "detector_name": self.detector_name,
                "sent_time": sent_time,
                "neutrino_time": data_enum.nu_time,
                "machine_time": data_enum.machine_time,
                "location": self.detector_loc,
                "status": data_enum.detector_status,
                "timing_series": data_enum.timing_series
            }),
            "SigTier": message_type('SigTier', {
                "_id": self.id_format("OBS", "SigTier"),
                "detector_name": self.detector_name,
                "sent_time": sent_time,
                "neutrino_time": data_enum.nu_time,
                "machine_time": data_enum.machine_time,
                "location": self.detector_loc,
                "p_value": data_enum.p_value,
                "status": data_enum.detector_status,
            }),
            "CoincidenceTier": message_type('CoincidenceTier', {
                "_id": self.id_format("OBS", "CoincidenceTier"),
                "detector_name": self.detector_name,
                "sent_time": sent_time,
                "neutrino_time": data_enum.nu_time,
                "machine_time": data_enum.machine_time,
                "location": self.detector_loc,
                "p_value": data_enum.p_value,
                "status": data_enum.detector_status,
            }),
            "Heartbeat": message_type('Heartbeat', {
                "_id": self.id_format("OBS", "Heartbeat"),
                "detector_name": self.detector_name,
                "sent_time": sent_time,
                "machine_time": data_enum.machine_time,
                "location": self.detector_loc,
                "status": data_enum.detector_status,
            }),

        }
        return messages[msg_type]

    def get_alert_schema(self, msg_type, sent_time, data_enum):
        message_type = namedtuple('message_type', ['topic_name', 'mgs'])
        messages = {
            "TimeTierAlert": message_type('TimeTierAlert', {
                "_id": self.id_format("ALERT", "TimeTierAlert"),
                "detector_names": data_enum.detectors,
                "sent_time": sent_time,
                "neutrino_times": data_enum.nu_times,
                "machine_times": data_enum.machine_times,
                "timing_series": data_enum.t_series,
                "locations": data_enum.locs,

            }),
            "SigTierAlert": message_type('SigTierAlert', {
                "_id": self.id_format("ALERT", "SigTierAlert"),
                "detector_name": data_enum.detectors,
                "sent_time": sent_time,
                "neutrino_times": data_enum.nu_times,
                "machine_times": data_enum.machine_times,
                "locations": data_enum.locs,
                "p_values": data_enum.p_vals,

            }),
            "CoincidenceTierAlert": message_type('CoincidenceTierAlert', {
                "_id": self.id_format("ALERT", "CoincidenceTierAlert"),
                "detector_names": data_enum.detectors,
                "sent_time": sent_time,
                "neutrino_times": data_enum.nu_times,
                "machine_times": data_enum.machine_times,
                "locations": data_enum.locs,
                "p_values": data_enum.p_vals,

            }),
        }
        return messages[msg_type]

### comment from Melih:
### get_alert_schema is almost the same as the get_obs_schema
### the only difference comes in when formatting the ID. 
### Since both these functions are backhand, we can easily merge them
###-----------
### Moreover, why do the ALERT messages have detector ids or status?

