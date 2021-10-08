"""
"""
from dotenv import load_dotenv
from datetime import datetime
from collections import namedtuple
import os, json
from pathlib import Path
import sys


def check_mongo_connection():
    pass


def check_hop_connection():
    pass


def set_env(env_path=None):
    """ Set environment
    Arguments
    ---------
    env_path : str (optional)
        path for the environment file.
        Use default settings if not given
    """
    dirname = os.path.dirname(__file__)
    default_env_path = os.path.dirname(__file__) + '/auxiliary/test-config.env'
    env = env_path or default_env_path
    load_dotenv(env)


def make_dir(path):
    if Path(path).is_dir():
        pass
    else:
        os.makedirs(path)


class TimeStuff:
    ''' SNEWS format datetime objects
    '''

    def __init__(self, env_path=None):
        set_env(env_path)
        self.snews_t_format = os.getenv("TIME_STRING_FORMAT")
        self.hour_fmt = "%H:%M:%S"
        self.date_fmt = "%y_%m_%d"
        self.get_datetime = datetime.utcnow()
        self.get_snews_time = lambda fmt=self.snews_t_format: datetime.utcnow().strftime(fmt)
        self.get_hour = lambda fmt=self.hour_fmt: datetime.utcnow().strftime(fmt)
        self.get_date = lambda fmt=self.date_fmt: datetime.utcnow().strftime(fmt)

    def str_to_datetime(self, nu_time):
        return datetime.strptime(nu_time, '%H %M %S %f')


def set_topic_state(which_topic, env_path=None):
    # check first to see if env already defined
    if os.getenv("ALERT_TOPIC") == None: set_env(env_path)
    Topics = namedtuple('Topics', ['topic_name', 'topic_broker'])
    topics = {
        'A': Topics('ALERT', os.getenv("ALERT_TOPIC")),
        'O': Topics('OBSERVATION', os.getenv("OBSERVATION_TOPIC")),
        'H': Topics('HEARTBEAT', os.getenv("OBSERVATION_TOPIC"))
    }
    return topics[which_topic.upper()]


# retrieve the detector properties
def retrieve_detectors(detectors_path=os.path.dirname(__file__) + "/auxiliary/detector_properties.json"):
    ''' Retrieve the name-ID-location of the
        participating detectors.
    '''
    # search for the pre-saved detectors file, create if not exist
    if not os.path.isfile(detectors_path):
        os.system(f'python {os.path.dirname(__file__)}/auxiliary/make_detector_file.py')

    with open(detectors_path) as json_file:
        detectors = json.load(json_file)

    # make a namedtuple
    Detector = namedtuple("Detector", ["name", "id", "location"])
    for k, v in detectors.items():
        detectors[k] = Detector(v[0], v[1], v[2])
    return detectors


def get_detector(detector, detectors_path=os.path.dirname(__file__) + "/auxiliary/detector_properties.json"):
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
    set_env()
    broker = os.getenv("HOP_BROKER")
    observation_topic = os.getenv("OBSERVATION_TOPIC")
    heartbeat_topic = os.getenv("OBSERVATION_TOPIC")
    alert_topic = os.getenv("ALERT_TOPIC")
    topic_type = f"Publish SNEWS {topic_type_} Messages"
    print(
        '#'.center(50, '#') +
        f'\n# {topic_type:^46} #\n'
        f'#{detector.name:_^48}#\n'
        f'#{str(detector.id) + "-" + detector.location:_^48}#\n' +
        '#'.center(50, '#') +
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


def display_gif():
    if isnotebook():
        from IPython.display import HTML, display
        giphy_snews = "https://raw.githubusercontent.com/SNEWS2/hop-SNalert-app/snews2_dev/hop_comms/auxiliary/snalert.gif"
        display(HTML(f'<img src={giphy_snews}>'))


def data_obs(machine_time=None, nu_time=None, p_value=None, timing_series=None,
             detector_status=None, false_mgs_id=None, **kwargs):
    """ default observation message data
    """
    keys = ['machine_time', 'neutrino_time', 'p_value', 'timing_series', 'detector_status', 'false_id']
    values = [machine_time, nu_time, p_value, timing_series, detector_status, false_mgs_id]
    # allow for keyword-args
    for k, v in kwargs.items():
        keys.append(k)
        values.append(v)
    zip_iterator = zip(keys, values)
    data_dict = dict(zip_iterator)
    return data_dict


def data_alert(p_vals=None, detectors=None, t_series=None, nu_times=None,
               ids=None, locs=None, status=None, machine_times=None):
    keys = ['p_vals', 'detectors', 't_series', 'neutrino_times', 'ids', 'locs', 'status', 'machine_times']
    values = [p_vals, detectors, t_series, nu_times, ids, locs, status, machine_times]
    return dict(zip(keys, values))

# Note from from Seb: :(
## Not working properly
# def run_parallel(nparallel=2):
#     """ Run publish & subscribe methods in parallel
#         Only works for notebooks. Requires ipyparallel
#         Arguments
#         ---------
#         nparallel : int
#             number of cells to run in parallel
#     """
#     if not isnotebook():
#         import sys
#         sys.exit('Cannot run processes in parallel')
#     # enable the extension in the current environment
#     os.system('ipcluster nbextension enable --user')
#     os.system(f'ipcluster start -n {nparallel}')
#     from ipyparallel import Client
#     rc = Client()
#     print("Run `%%px -a -t 0` magic command on the notebook!")
#     return None
