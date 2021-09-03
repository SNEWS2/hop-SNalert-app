import snews_utils
from collections import namedtuple
from snews_utils import TimeStuff

class Message_Schema():
    def __init__(self, env_path=None, detector='Detector0'):
        self.detector = snews_utils.get_detector(detector)
        self.detector_name = self.detector.name
        self.detector_loc = self.detector.loc
        self.times = TimeStuff(env_path)

    def id_format(self, topic_type):
        """ Returns formatted message ID
            time format should always be same for all detectors
        """
        date_time = self.times.get_snews_time(fmt="%y/%m/%d_%H:%M:%S")
        return f'{self.detector.id}_{topic_type}_{date_time}'

    def get_obs_schema(self, type, data_enum, sent_time):

        message_type = namedtuple('message_type', ['topic_name', 'mgs'])
        messages = {
            "Test": message("Test", {
                "_id": id_format(self.detector_name, "Test"),
                "detector_name": self.detector_name,
                "sent_time": sent_time,
                "neutrino_time": data_enum.nu_t,
                "machine_time": data_enum.machine_t,
                "location": self.detector_loc,
                "p_value": data_enum.p_value,
                "status": data_enum.detector_status,
            }),
            "TimeTier": message('TimeTier',{
                "_id": id_format(self.detector_name, "TimeTier"),
                "detector_name": self.detector_name,
                "sent_time": sent_time,
                "neutrino_time": data_enum.nu_t,
                "machine_time": data_enum.machine_t,
                "location": self.detector_loc,
                "status": data_enum.detector_status,
                "timing_series_series": data_enum.timing_series

            }),
            "SigTier": message('SigTier',{
                "_id": id_format(self.detector_name, "SigTier"),
                "detector_name": self.detector_name,
                "sent_time": sent_time,
                "neutrino_time": data_enum.nu_t,
                "machine_time": data_enum.machine_t,
                "location": self.detector_loc,
                "p_value": data_enum.p_value,
                "status": data_enum.detector_status,
            }),
            "CoincidinceTier": message('CoincidinceTier', {
                "_id": id_format(self.detector_name, "CoincidinceTier"),
                "detector_name": self.detector_name,
                "sent_time": sent_time,
                "neutrino_time": data_enum.nu_t,
                "machine_time": data_enum.machine_t,
                "location": self.detector_loc,
                "p_value": data_enum.p_value,
                "status": data_enum.detector_status,
            }),

        }

        return messages[type]
