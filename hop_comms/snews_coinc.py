import snews_utils
from snews_db import Storage
import os
# from datetime import datetime
import time
from hop_pub import Publish_Alert


class Decider:
    """
        Decider class for supernova alerts
    """

    def __init__(self, env_path=None):
        snews_utils.set_env(env_path)
        self.storage = Storage(drop_dbs=False)
        self.topic_type = "CoincidenceTier"
        self.coinc_treshold = float(os.getenv('COINCIDENCE_THRESHOLD'))
        self.mgs_expiration = int(os.getenv('MSG_EXPIRATION'))
        self.coinc_cache = self.storage.coincidence_tier_cache
        self.Alert = Publish_Alert()
        self.times = snews_utils.TimeStuff(env_path)

    def check_for_coincidence(self):
        ''' Main body of the class. Reads the 
            mongodb as a stream to look for coincidences.
        '''
        with self.coinc_cache.watch() as stream:
            # should it be: for mgs in stream ?
            while self.storage.empty_coinc_cache():
                print('Nothing here, please wait...')
                time.sleep(10)
            i = 0
            for doc in stream:
                self.storage.keep_cache_clean()
                print('Incoming message !!!')
                mgs = doc['fullDocument']
                print(mgs)
                if i == 0:
                    initial_nu_time = self.times.str_to_datetime(mgs['neutrino_time'])
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
                    curr_nu_time = self.times.str_to_datetime(mgs['neutrino_time'])
                    curr_detector = mgs['detector_name']
                    delta_t = (curr_nu_time - initial_nu_time).total_seconds()
                    print(delta_t)

                    if old_detector != curr_detector and delta_t <= self.coinc_treshold:
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
                    # coinc is broken
                    else:
                        if len(detectors) > 1:
                            print('Publishing Alert to SNEWS')
                            data_enum = snews_utils.data_enum_alert(p_vals=p_vals,detectors=detectors,nu_times=delta_ts)
                            self.Alert.publish(type=self.topic_type,data_enum=data_enum)


                        print('reseting coincidence counter')
                        i = 0
                        initial_nu_time = self.times.str_to_datetime(mgs['neutrino_time'])
                        old_detector = mgs['detector_name']
                        old_loc = mgs['location']
                        p_vals = [mgs['p_value']]
                        detectors = [old_detector]
                        nu_times = [mgs['neutrino_time']]
                        delta_ts = [0]
                        ids = [mgs['_id']]
                        i += 1
