import snews_utils
from snews_db import Storage
import os
from datetime import datetime
import time


class Decider:

    def __init__(self, env=None):
        snews_utils.set_env()
        self.storage = Storage(drop_dbs=False)
        self.coinc_treshold = float(os.getenv('COINCIDENCE_THRESHOLD'))
        self.mgs_expiration = int(os.getenv('MSG_EXPIRATION'))
        self.coinc_cache = self.storage.coincidence_tier_cache

    def check_for_coincidence(self):
        with self.coinc_cache.watch() as stream:
            # should it be: for mgs in stream ?
            while self.storage.empty_coinc_cache():
                print('nothing here, pls wait...')
                time.sleep(10)
            i = 0
            for doc in stream:
                self.storage.keep_cache_clean()
                print('Incoming message !!!')
                mgs = doc['fullDocument']
                print(mgs)
                if i == 0:
                    initial_nu_time = datetime.strptime(mgs['neutrino_time'], '%H %M %S %f')
                    old_detector = mgs['detector_name']
                    old_loc = mgs['location']
                    p_vals = [mgs['p_value']]
                    detectors = [old_detector]
                    nu_times = [mgs['neutrino_time']]
                    delta_ts = [0]
                    ids = [mgs['_id']]
                    i += 1

                elif i != 0:
                    curr_loc = mgs['location']
                    curr_p_val = mgs['p_value']
                    curr_nu_time = datetime.strptime(mgs['neutrino_time'], '%H %M %S %f')
                    curr_detector = mgs['detector_name']
                    delta_t = (curr_nu_time - initial_nu_time).total_seconds()
                    print(delta_t)

                    if old_loc != curr_loc and old_detector != curr_detector and delta_t <= self.coinc_treshold:
                        p_vals.append(curr_p_val)
                        detectors.append(curr_detector)
                        nu_times.append(mgs['neutrino_time'])
                        ids.append(mgs['_id'])
                        delta_ts.append(delta_t)
                        old_detector = curr_detector
                        old_loc = curr_loc
                        i += 1
                        print('Detectors:')
                        print(detectors)
                        print('Delta time to initial nu signal:')
                        print(delta_ts)
                        print('P_vals:')
                        print(p_vals)
                        print('')
                    else:
                        i = 0
                        initial_nu_time = datetime.strptime(mgs['neutrino_time'], '%H %M %S %f')
                        old_detector = mgs['detector_name']
                        old_loc = mgs['location']
                        p_vals = [mgs['p_value']]
                        detectors = [old_detector]
                        nu_times = [mgs['neutrino_time']]
                        delta_ts = [0]
                        ids = [mgs['_id']]
                        i += 1
