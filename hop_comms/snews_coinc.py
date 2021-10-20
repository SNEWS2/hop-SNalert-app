from . import snews_utils
from .snews_db import Storage
import os, click
from datetime import datetime
import time
from .hop_pub import Publish_Alert
import numpy as np


# TODO Need to turn detector names into a unique arr
# TODO Implement silver/gold
class CoincDecider:
    """ CoincDecider class for Supernova alerts (Coincidence Tier)
        
    Parameters
    ----------
    env_path : str, optional
        user can give the path a specific SNEWS env file, 
        defaults to None ./auxiliary/test-config.env)
    
    """

    def __init__(self, env_path=None, use_local=False):
        snews_utils.set_env(env_path)

        self.storage = Storage(drop_db=False, use_local=use_local)
        self.topic_type = "CoincidenceTierAlert"
        self.coinc_threshold = float(os.getenv('COINCIDENCE_THRESHOLD'))
        # self.mgs_expiration = float(os.getenv('MSG_EXPIRATION'))
        self.mgs_expiration = 300
        self.coinc_cache = self.storage.coincidence_tier_cache
        self.alert = Publish_Alert(use_local=True)
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
        """ Appends coincidence arrays when there is a coincident signal

        Parameters
        ----------
        mgs : `dict`
            dictionary of the SNEWS message

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
        """ Resets coincidence arrays if coincidence is broken

        """
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
        """ Sets up the initial signal

        Parameters
        ----------
        mgs : `dict`
            dictionary of the SNEWS message

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
        """ Remove the information at a given index

        Parameters
        ----------
        index : `int`
            The index in which the information is removed

        """
        self.detectors.pop(index)
        self.ids.pop(index)
        self.nu_times.pop(index)
        self.delta_ts.pop(index)
        self.p_vals.pop(index)
        self.machine_times.pop(index)

    def reset_cache(self):
        """ Resets mongo cache and all coincidence arrays if coincidence is broken

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
        """ 
        Checks new message in the stream, 
        if message is within SN time window (10sec) 
        it is added to the coincidence list, if not 
        coincidence is broken. Then the publish method is called. 
        Finally a new stream and coincicede list is made

        Parameters
        ----------
        mgs : `dict`
            dictionary of the SNEWS message


        """
        if self.cache_reset:
            pass

        if self.counter != 0:
            self.curr_nu_time = self.times.str_to_hr(mgs['neutrino_time'])
            self.curr_loc = mgs['location']
            self.old_detector = mgs['detector_name']
            self.delta_t = (self.curr_nu_time - self.initial_nu_time).total_seconds()

            if self.delta_t <= self.coinc_threshold:
                self.append_arrs(mgs)
                click.secho('got something'.upper(), fg='white', bg='red')
                print(f'{self.delta_ts}')
                # self.counter += 1
            # should the same experiment sends two messages one after the other
            # the coincidence would break since curr_loc == old_loc
            # do we want this?
            elif self.delta_t > self.coinc_threshold:
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
        """
        Waits for a new message, if a new message does not come
        in before 120sec then coincidence is broken.
        Publishing method is called and then the stream and cache are reset

        """
        curr_cache_len = self.storage.coincidence_tier_cache.count()
        stagnant_cache = True
        t0 = time.time()
        click.secho('waiting..'.upper(), fg='cyan', bold=True, )
        while stagnant_cache:
            t1 = time.time()
            delta_t = t1 - t0
            self.in_cache_retract()
            if self.storage.coincidence_tier_cache.count() > curr_cache_len and delta_t < self.mgs_expiration:
                self.counter += 1
                break
            # for every minute
            # if np.round(delta_t) > 10 and np.round(delta_t)% 60 == 0:
            #     click.secho(
            #         f'Here is the current coincident list\n',
            #         fg='magenta', bold=True, )
            #     click.secho(
            #         f'Total Number of detectors: {np.unique(self.detectors)} \n',
            #         fg='magenta', bold=True, )
            #     click.secho(
            #         f'Total number of coincident events: {len(self.ids)}\n',
            #         fg='magenta', bold=True, )
            elif delta_t > self.mgs_expiration:
                click.secho('\nWaited too long !!'.upper(), fg='cyan', bold=True)
                self.coinc_broken = True
                self.pub_alert()
                print('\nResetting cache')
                self.reset_cache()
                # Run recursion
                click.secho('\n\nStarting new stream..\n\n'.upper(), bold=True, fg='bright_white', underline=True)
                self.run_coincidence()


    def in_cache_retract(self):
        """ 
        loops through false warnings collection looks for 
        coincidence tier false warnings, if a warning is found,
        it then loops through coincidence cache, if the false message
        is then all its corresponding features are deleted
        from the coincidence arrays.

        """
        if self.storage.empty_false_warnings():
            # print('No false messages...yet')
            pass

        if len(self.ids) == 0:
            # print('cache is empty')
            pass

        for mgs in self.storage.get_false_warnings():
            # Delete N many false messages
            if mgs['N_look_for_latest'] != 0 and (mgs['which_tier'] == 'CoincidenceTier' or mgs['which_tier'] == 'ALL'):
                i = len(self.ids) - 1
                drop_detector = mgs['detector_name']
                delete_n_many = mgs['N_look_for_latest']
                if mgs['N_look_for_latest'] == 'ALL':
                    delete_n_many = self.detectors.count(drop_detector)
                print(
                    f'\nDropping latest message(s) from {drop_detector}\nRetracting: {delete_n_many} messages')
                for detector_name in reversed(self.detectors):
                    if delete_n_many > 0 and detector_name == drop_detector:
                        delete_n_many -= 1
                        self.kill_false_element(index=i)
                    i -= 1
                query = {'_id': mgs['_id']}
                self.storage.false_warnings.delete_one(query)
                print(f'\nTotal Number of coincident events left: {len(self.ids)}')

            if mgs['false_id'] != None and mgs['false_id'].split('_')[1] == 'CoincidenceTier':
                false_id = mgs['false_id']
                i = 0
                for id in self.ids:
                    if false_id == id:
                        self.kill_false_element(index=i)
                        print(f'\nFalse mgs found {id}\nPurging it from coincidence list\n')
                        break
                        # print(f'\nNew list of coincident detectors:\n{self.detectors}')
                    i += 1
                query = {'_id': mgs['_id']}
                self.storage.false_warnings.delete_one(query)

    def pub_alert(self):
        """ When the coincidence is broken publish alert
            if there were more than 1 detectors in the 
            given coincidence window

        """
        unique_detectors = np.unique(self.detectors)
        if self.coinc_broken and len(unique_detectors) > 1:
            click.secho(f'{"=" * 57}', fg='bright_red')
            alert_data = snews_utils.data_alert(detectors=unique_detectors,
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
                SNEWS_message = doc['fullDocument']
                click.secho(f'{"-" * 57}', fg='bright_blue')
                click.secho('Incoming message !!!'.upper(), bold=True, fg='red')
                click.secho(f'{SNEWS_message["_id"]}'.upper(), fg='bright_green')
                self.set_initial_signal(SNEWS_message)
                self.check_for_coinc(SNEWS_message)
                print(f'Detectors: {self.detectors}')
                self.waited_long_enough()
