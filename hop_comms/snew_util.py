from dotenv import load_dotenv
from datetime import datetime
from collections import namedtuple
import os


def set_env(env_path):
    load_dotenv(env_path)


def check_mongo_connection():
    pass


def check_hop_connection():
    pass


class TimeStuff:
    def __init__(self, env):
        set_env(env)
        self.snews_t_format = os.getenv("TIME_STRING_FORMAT")
        self.hr = "%H:%M:%S"
        self.date = "%y_%m_%d"

    def get_snews_time_str(self):
        return datetime.utcnow().strftime(self.snews_t_format)

    def get_hr_str(self):
        return datetime.utcnow().strftime(self.hr)

    def get_date_str(self):
        return datetime.utcnow().strftime(self.date)


def set_topic_state(which_topic):
    Topics = namedtuple('Topics', ['topic_name', 'topic_broker'])
    topics = {
        'ALERT': Topics('ALERT', 'kafka://kafka.scimma.org/snews.alert-test'),
        'OBSERVATION': Topics('OBSERVATION', 'kafka://kafka.scimma.org/snews.experiments-test')
    }
    if which_topic == 'A':
        return topics['ALERT']
    elif which_topic == 'O':
        return topics['OBSERVATION']
