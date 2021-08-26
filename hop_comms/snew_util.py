from dotenv import load_dotenv
from datetime import datetime

'''
loads SNEWS env 
'''


def set_env(env_path):
    load_dotenv(env_path)


def check_mongo_connection():
    pass


def check_hop_connection():
    pass


class Time_Stuff:
    def __init__(self):
        self.snews_t_format = os.getenv("TIME_STRING_FORMAT")
        self.hr = "%H:%M:%S"
        self.date = "%y_%m_%d"

    def get_snews_time_str(self):
        return datetime.utcnow().strftime(self.snews_t_format)

    def get_hr_str(self):
        return datetime.utcnow().strftime(self.hr)

    def get_date_str(self):
        return datetime.utcnow().strftime(self.date)