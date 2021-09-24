import snews_utils
from snews_db import Storage
import os
# from datetime import datetime
import time
from hop_pub import Publish_Alert


class CoincDecider:
    """
        CoincDecider class for supernova alerts (Coincidence Tier)
        param: env_path
    """

    def __init__(self, env_path=None):
        snews_utils.set_env(env_path)

        self.storage = Storage(drop_dbs=False)
        self.topic_type = "CoincidenceTier"
        self.coinc_threshold = float(os.getenv('COINCIDENCE_THRESHOLD'))
        self.mgs_expiration = int(os.getenv('MSG_EXPIRATION'))
        self.coinc_cache = self.storage.coincidence_tier_cache
        self.alert = Publish_Alert()
        self.times = snews_utils.TimeStuff(env_path)

        self.counter = 0

        self.initial_nu_time = None
        self.old_detector = None
        self.old_loc = None

        self.curr_nu_time = None
        self.curr_detector = None
        self.curr_loc = None

        self.delta_t = None

        self.delta_ts = []
        self.detectors = []
        self.nu_times = []
        self.locs = []
        self.machine_times = []
        self.status = []
        self.p_vals = []

        self.coinc_broken = False

    def append_arrs(self, mgs):
        self.nu_times.append(mgs['neutrino_time'])
        self.detectors.append(mgs['detector_name'])
        self.machine_times.append(mgs['machine_time'])
        self.p_vals.append(mgs['p_value'])
        self.status.append(mgs['status'])
        if self.counter == 0:
            self.delta_ts.append(0)
        elif self.counter != 0:
            self.delta_ts.append(self.delta_t)

    def reset_arr(self):
        if self.coinc_broken:
            self.delta_ts = []
            self.detectors = []
            self.nu_times = []
            self.locs = []
            self.machine_times = []
            self.status = []
            self.p_vals = []
        else:
            pass

    def set_initial_signal(self, mgs):
        if self.counter == 0:
            self.initial_nu_time = self.times.str_to_datetime(mgs['neutrino_time'])
            self.old_loc = mgs['location']
            self.old_detector = mgs['detector_name']
            self.append_arrs(mgs)

        else:
            pass

    def check_for_conic(self, mgs):
        if self.counter != 0:
            self.curr_nu_time = self.times.str_to_datetime(mgs['neutrino_time'])
            self.curr_loc = mgs['location']
            self.old_detector = mgs['detector_name']
            self.delta_t = (self.curr_nu_time - self.initial_nu_time).total_seconds()

            if self.delta_t <= self.coinc_threshold and self.curr_loc != self.old_loc:
                self.append_arrs(mgs)
                print('got something')
                print(f'{self.delta_ts}')
                pass
            elif self.delta_t > self.coinc_threshold or self.curr_loc == self.old_loc:
                print('Coincidence is broken, checking to see if an ALERT can be published.../n/n')
                self.coinc_broken = True
        else:
            pass

    def pub_alert(self):
        if self.coinc_broken and len(self.detectors) > 1:
            alert_enum = snews_utils.data_enum_alert(detectors=self.detectors, p_vals=self.p_vals,
                                                     nu_times=self.nu_times, machine_times=self.machine_times)
            self.alert.publish(type=self.topic_type, data_enum=alert_enum)
            print('published alert!!!')
        else:
            pass

    def run_coincidence(self):
        ''' Main body of the class. Reads the 
            mongodb as a stream to look for coincidences.
        '''
        with self.coinc_cache.watch() as stream:
            # should it be: for mgs in stream ?
            while self.storage.empty_coinc_cache():
                print('Nothing here, please wait...')
                time.sleep(10)
            for doc in stream:
                self.storage.keep_cache_clean()
                print('Incoming message !!!')
                mgs = doc['fullDocument']
                print(mgs)
                self.set_initial_signal(mgs)
                self.check_for_conic(mgs)
                self.pub_alert()
                if self.coinc_broken:
                    self.counter = 0
                    self.reset_arr()
                    self.set_initial_signal(mgs)
                self.counter += 1
