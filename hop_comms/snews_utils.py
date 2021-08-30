from dotenv import load_dotenv
from datetime import datetime
from collections import namedtuple
import os, json


def check_mongo_connection():
    pass


def check_hop_connection():
    pass


def set_env(self, env_path=None):
    """ Set environment
    Arguments
    ---------
    env_path : str (optional)
        path for the environment file.
        Use default settings if not given
    """
    env = env_path or './test-config.env'
    load_dotenv(env)


def make_dir(path):
    if os.path.isdir(path):
        pass
    else:
        os.makedirs(path)


class TimeStuff:
    ''' SNEWS format datetime objects
    '''

    def __init__(self, env=None):
        set_env(env)
        self.snews_t_format = os.getenv("TIME_STRING_FORMAT")
        self.hour_fmt = "%H:%M:%S"
        self.date_fmt = "%y_%m_%d"

        self.get_datetime = datetime.utcnow()
        self.get_snews_time = lambda fmt=self.snews_t_format: datetime.utcnow().strftime(fmt)
        self.get_hour = lambda fmt=self.hour_fmt: datetime.utcnow().strftime(fmt)
        self.get_date = lambda fmt=self.date_fmt: datetime.utcnow().strftime(fmt)


def set_topic_state(which_topic,env=None):
    set_env(env)
    alert_broker = os.getenv('ALERT_TOPIC')
    obs_broker = os.getenv('OBSERVATION_TOPIC')
    Topics = namedtuple('Topics', ['topic_name', 'topic_broker'])
    topics = {
        'ALERT': Topics('ALERT', alert_broker),
        'OBSERVATION': Topics('OBSERVATION', obs_broker)
    }
    if which_topic == 'A':
        return topics['ALERT']
    elif which_topic == 'O':
        return topics['OBSERVATION']


# retrieve the detector properties
def retrieve_detectors(detectors_path="./detector_properties.json"):
    ''' Retrieve the name-ID-location of the
        participating detectors.
    '''
    # search for the pre-saved detectors file, create if not exist
    if not os.path.isfile(detectors_path):
        os.system(f'python make_detector_file.py')

    with open(detectors_path) as json_file:
        detectors = json.load(json_file)

    # make a namedtuple
    Detector = namedtuple("Detector", ["name", "id", "location"])
    for k, v in detectors.items():
        detectors[k] = Detector(v[0], v[1], v[2])
    return detectors


def get_detector(detector, detectors_path="./detector_properties.json"):
    """ Return the selected detector properties
    """
    Detector = namedtuple("Detector", ["name", "id", "location"])
    if isinstance(detector, Detector): return detector  # not needed?
    # search for the detector name in `detectors`
    detectors = retrieve_detectors(detectors_path)
    if isinstance(detector, str):
        try:
            return detectors[detector]
        except KeyError:
            print(f'{detector} is not a valid detector!')
            return detectors['TEST']


def summarize(detector, topic_type_, env_path=None):
    """ Summarize the current configuration
    """
    import hop, snews, sys
    set_env(env_path)
    broker = os.getenv("HOP_BROKER")
    observation_topic = os.getenv("OBSERVATION_TOPIC")
    heartbeat_topic = os.getenv("OBSERVATION_TOPIC")
    alert_topic = os.getenv("ALERT_TOPIC")
    topic_type = f"Publish SNEWS {topic_type_} Messages"
    print(
        '#'.ljust(50, '#') +
        f'\n# {topic_type:^46} #\n'
        f'#{detector.name:_^48}#\n'
        f'#{str(detector.id) + "-" + detector.location:_^48}#\n' +
        '#'.center(51, '#') +
        f'\nYour Python version:\n {sys.version}\n'
        f'Current hop-client version:{hop.__version__}\n'
        f'             snews version:{snews.__version__}\n\n'
        f'Publishing to {broker}\n'
        f'Observation Topic:\n==> {observation_topic}\n'
        f'Heartbeat Topic:\n==> {heartbeat_topic}\n\n')


def isnotebook():
    """ Tell if the script is running on a notebook
    """
    try:
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':
            return True  # Jupyter notebook or qtconsole
        elif shell == 'TerminalInteractiveShell':
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False  # Probably standard Python interpreter


def get_logger(scriptname, logfile_name):
    import logging
    # Gets or creates a logger
    logger = logging.getLogger(scriptname)

    # set log level
    logger.setLevel(logging.INFO)
    # define file handler and set formatter
    file_handler = logging.FileHandler(logfile_name)
    formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
    file_handler.setFormatter(formatter)
    # add file handler to logger
    logger.addHandler(file_handler)
    return logger