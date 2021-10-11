from . import snews_utils
from .snews_db import Storage
import os, click
# from datetime import datetime
import time
from .hop_pub import Publish_Alert


# comment: we should keep in mind that lists [], and numpy arrays np.array([])
# behave differently in calculations e.g. np.array([1,2,3])*2 = np.array([2,4,6])
# whereas [1,2,3]*2 = [1,2,3,1,2,3]
# it is more efficient to append to lists but we should be careful when performing
# some calculations with the p-values or delta ts.

class CoincDecider:
    """
        CoincDecider class for supernova alerts (Coincidence Tier)
        param: env_path, user can give the path a specific SNEWS env file, defaults to None ./auxiliary/test-config.env)
    """

    def __init__(self, env_path=None):
        """Constructor method
        """
        snews_utils.set_env(env_path)

        self.storage = Storage(drop_dbs=False)
        self.topic_type = "CoincidenceTierAlert"
        self.coinc_threshold = float(os.getenv('COINCIDENCE_THRESHOLD'))
        self.mgs_expiration = float(os.getenv('MSG_EXPIRATION'))
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

        self.ids = []
        self.delta_ts = []
        self.detectors = []
        self.nu_times = []
        self.machine_times = []
        self.p_vals = []

        self.coinc_broken = False

        self.cache_reset = False

    def append_arrs(self, mgs):
        """Appends coincidence arrays when there is a coincident signal
        :param mgs: SNEWS message
        :mgs type: dict
        """
        self.nu_times.append(mgs['neutrino_time'])
        self.detectors.append(mgs['detector_name'])
        self.machine_times.append(mgs['machine_time'])
        self.p_vals.append(mgs['p_value'])
        self.ids.append(mgs['_id'])
        if self.counter == 0:
            self.delta_ts.append(0)
        elif self.counter != 0:
            self.delta_ts.append(self.delta_t)

    def reset_arr(self):
        """Resets coincidence arrays if coincidence is broken"""
        if self.coinc_broken:
            self.ids = []
            self.delta_ts = []
            self.detectors = []
            self.nu_times = []
            self.machine_times = []
            self.p_vals = []
        else:
            pass

    def set_initial_signal(self, mgs):
        """Sets up the initial signal
        :param mgs: SNEWS message
        :mgs type: dict
        """
        if self.counter == 0:
            print('Setting initial values')
            self.initial_nu_time = self.times.str_to_hr(mgs['neutrino_time'])
            self.old_loc = mgs['location']
            self.old_detector = mgs['detector_name']
            self.append_arrs(mgs)
            # self.delta_t = 0
            self.coinc_broken = False
            self.cache_reset = False
        else:
            pass

    def kill_false_element(self, index):
        """Sets up the initial signal
        :param mgs: SNEWS message
        :mgs type: dict
        """
        self.detectors.pop(index)
        self.ids.pop(index)
        self.nu_times.pop(index)
        self.delta_ts.pop(index)
        self.p_vals.pop(index)
        self.machine_times.pop(index)

    def reset_cache(self):
        """Resets mongo cache and all coincidence arrays if coincidence is broken
        """
        if self.coinc_broken:
            self.counter = 0
            self.reset_arr()
            self.storage.purge_cache(coll='CoincidenceTier')
            self.coinc_broken = False
            self.delta_t = None
            self.cache_reset = True
        else:
            pass

    def check_for_coinc(self, mgs):
        """Checks new message in the stream, if message is within SN time window (10sec) it is added to the coincidence list,
        if not coincidence is broken. Then the publish method is called. Finally a new stream and coincicede list is made
        :param mgs: SNEWS message
        :mgs type: dict
        """
        if self.cache_reset:
            pass

        if self.counter != 0:
            self.curr_nu_time = self.times.str_to_hr(mgs['neutrino_time'])
            self.curr_loc = mgs['location']
            self.old_detector = mgs['detector_name']
            self.delta_t = (self.curr_nu_time - self.initial_nu_time).total_seconds()

            if self.delta_t <= self.coinc_threshold and self.curr_loc != self.old_loc:
                self.append_arrs(mgs)
                click.secho('got something'.upper(), fg='white', bg='red')
                print(f'{self.delta_ts}')
                # self.counter += 1
            # should the same experiment sends two messages one after the other
            # the coincidence would break since curr_loc == old_loc
            # do we want this?
            elif self.delta_t > self.coinc_threshold or self.curr_loc == self.old_loc:
                if self.delta_t > self.coinc_threshold:
                    print('Outside SN window')
                print('Coincidence is broken, checking to see if an ALERT can be published...\n\n')
                self.coinc_broken = True
                self.pub_alert()
                print('Resetting the cache')
                self.reset_cache()
                self.set_initial_signal(mgs)
                self.storage.coincidence_tier_cache.insert_one(mgs)
                # Start recursion
                click.secho('Starting new stream..'.upper(), bold=True, fg='bright_white', underline=True)
                self.counter += 1
                self.run_coincidence()


        else:
            pass

    def waited_long_enough(self):
        """Waits for a new message, if a new message does not come in before 120sec then coincidence is broken.
        Publishing method is called and then the stream and cache are reset
        """
        curr_cache_len = self.storage.coincidence_tier_cache.count()
        stagnant_cache = True
        t0 = time.time()
        click.secho('waiting..'.upper(), fg='cyan', bold=True, italic=True)
        while stagnant_cache:
            t1 = time.time()
            delta_t = t1 - t0
            self.in_cache_retract()
            if self.storage.coincidence_tier_cache.count() > curr_cache_len and delta_t < self.mgs_expiration:
                self.counter += 1
                break
            elif delta_t > self.mgs_expiration:
                print('Waited too long !!')
                self.coinc_broken = True
                self.pub_alert()
                print('Resetting cache')
                self.reset_cache()
                # Run recursion
                click.secho('Starting new stream..\n\n'.upper(), bold=True, fg='bright_white', underline=True)
                self.run_coincidence()

    def in_cache_retract(self):
        """loops through false warnings collection looks for coincidence tier false warnings, if a warning is found,
        it then loops through coincidence cache, if the false message is then all its corresponding features are deleted
        from the coincidence arrays."""
        if self.storage.empty_false_warnings():
            # print('No false messages...yet')
            pass
        if len(self.ids) == 0:
            # print('cache is empty')
            pass
        for mgs in self.storage.get_false_warnings():
            if mgs['type'] == 'CoincidenceTier':
                false_id = mgs['false_id']
                i = 0
                for id in self.ids:
                    if false_id == id:
                        print(f'False mgs found {id}\nPurging coincidence list')
                        self.kill_false_element(index=i)
                    i += 1

    def pub_alert(self):
        """ When the coincidence is broken publish alert
            if there were more than 1 detectors in the 
            given coincidence window
        """
        if self.coinc_broken and len(self.detectors) > 1:
            click.secho(f'{"=" * 57}', fg='bright_red')
            alert_data = snews_utils.data_alert(detectors=self.detectors,
                                                ids=self.ids,
                                                p_vals=self.p_vals,
                                                nu_times=self.nu_times,
                                                machine_times=self.machine_times)
            self.alert.publish(msg_type=self.topic_type, data=alert_data)
            click.secho('Published an Alert!!!'.upper(), bg='bright_green', fg='red')
            click.secho(f'{"=" * 57}', fg='bright_red')
        else:
            print('Nothing to send :(')
            pass

    def run_coincidence(self):
        ''' Main body of the class. Reads the 
            mongodb as a stream to look for coincidences.
        '''
        with self.coinc_cache.watch() as stream:
            # should it be: for mgs in stream ?
            if self.storage.empty_coinc_cache():
                click.secho(f'{"-" * 57}', fg='bright_blue')
                print('Nothing here, please wait...')

            for doc in stream:
                click.secho(f'{"-" * 57}', fg='bright_blue')
                click.secho('Incoming message !!!'.upper(), bold=True, fg='red')
                mgs = doc['fullDocument']
                click.secho(f'{mgs["_id"]}'.upper(), italic=True, fg='bright_green')
                self.set_initial_signal(mgs)
                self.check_for_coinc(mgs)
                print(f'Detectors: {self.detectors}')
                self.waited_long_enough()
